import os
from pathlib import Path
import numpy as np
import h5py
import yaml
from camp.utils import find_nearest, missing_elements


class Ion:

    def __init__(self, fragments_config_file: str, fragment_name: str):
        with open(fragments_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        self.tof_start = cfg['fragments'][fragment_name]['tof_start']
        self.tof_end = cfg['fragments'][fragment_name]['tof_end']
        self.center_x = cfg['fragments'][fragment_name]['center_x']
        self.center_y = cfg['fragments'][fragment_name]['center_y']


class trace:

    def __init__(self, values, label=None, unit=None):
        self.array = np.array(values)
        self.length = len(self.array)
        self.label = label
        self.unit = unit

    def __str__(self):
        return str(self.array)


class TimePixRun:
    file_system = 'core'
    config_data_path_file = Path('../config/beamtime.yaml')
    fragments_config_file = Path('../config/fragments.yaml')
    event_type = 'raw'

    def __init__(self, run_number: int):
        assert isinstance(run_number, int)
        self.run_number = run_number
        self.hdf_file = self.__generate_hdf_filename()

    def __generate_hdf_filename(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        timepix_hdf_path = cfg['path'][self.file_system] + cfg['timepix']
        try:
            file_start = "run_" + str(self.run_number).zfill(4)
            hdf_file = [i for i in os.listdir(timepix_hdf_path) if
                        os.path.isfile(os.path.join(timepix_hdf_path, i)) and i.startswith(
                            file_start) and not i.endswith(
                            'rawOnly.hdf5')][0]
            hdf_file_complete_path = timepix_hdf_path + hdf_file
            assert os.path.isfile(hdf_file_complete_path), 'File does not exist!'
            return hdf_file_complete_path
        except IndexError:
            print("Run", self.run_number, "does not exist!")

    def get_number_of_trains_from_hdf(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            self.number_of_trains = len(h_file['tpx3Times/triggerNr'][:])
        return self.number_of_trains

    def get_number_of_raw_events(self):
        tof, _, _ = self.get_tof_x_y()
        self.number_of_raw_events = tof.length
        return self.number_of_raw_events

    def get_pp_delay(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        pp_delay_path = cfg['path'][self.file_system] + cfg['pp_delay']
        assert os.path.isfile(pp_delay_path), 'File does not exist!'
        try:
            with open(pp_delay_path, 'r') as ymlfile:
                yml = yaml.safe_load(ymlfile)
            self.pp_delay = yml['pp_delay'][self.run_number]
            return self.pp_delay
        except KeyError:
            print("Run", self.run_number, "does not have pump-probe delay.")
            return None

    def get_tof_x_y(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            tof = trace(h_file[str(self.event_type) + '/tof'][:], label='ToF', unit='s')
            x_pos = trace(h_file[str(self.event_type) + '/x'][:], label='x pos', unit='px')
            y_pos = trace(h_file[str(self.event_type) + '/y'][:], label='y pos', unit='px')
        self.__assert_equal_length([tof, x_pos, y_pos])
        return tof, x_pos, y_pos

    def get_tof_x_y_sliced_by_tof_interval(self, tof_start=0, tof_end=0.1):
        tof, x_pos, y_pos = self.get_tof_x_y()
        sliced_x_pos = self.__slice_by_tof(x_pos, tof, tof_start, tof_end)
        sliced_y_pos = self.__slice_by_tof(y_pos, tof, tof_start, tof_end)
        sliced_tof = self.__slice_by_tof(tof, tof, tof_start, tof_end)
        self.__assert_equal_length([sliced_tof, sliced_x_pos, sliced_y_pos])
        return sliced_tof, sliced_x_pos, sliced_y_pos

    def get_tof_x_y_of_fragment(self, fragment_name):
        fragment = Ion(self.fragments_config_file, fragment_name)
        return self.get_tof_x_y_sliced_by_tof_interval(fragment.tof_start, fragment.tof_end)

    def get_tof_x_y_of_single_trigger(self, trigger_nr):
        with h5py.File(self.hdf_file, 'r') as h_file:
            nr = h_file[str(self.event_type) + '/nr'][:]
            tof = trace(h_file[str(self.event_type) + '/tof'][nr == trigger_nr], label='ToF', unit='s')
            x_pos = trace(h_file[str(self.event_type) + '/x'][nr == trigger_nr], label='x pos', unit='px')
            y_pos = trace(h_file[str(self.event_type) + '/y'][nr == trigger_nr], label='y pos', unit='px')
        self.__assert_equal_length([tof, x_pos, y_pos])
        return tof, x_pos, y_pos

    def __slice_by_tof(self, array, tof, tof_start, tof_end):
        return trace(array.array[np.logical_and(tof.array > tof_start, tof.array < tof_end)],
                     label=array.label, unit=array.unit)

    def __assert_equal_length(self, list_of_obj):
        for i in range(len(list_of_obj) - 1):
            assert list_of_obj[0].length == list_of_obj[i + 1].length

    def get_trainIDs(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            x2_trainIDs = h_file['x2Times/bunchID'][:]
            x2_timestamps = h_file['x2Times/ns'][:]
            tpx3_triggerNrs = h_file['tpx3Times/triggerNr'][:]
            tpx3_timestamps = h_file['tpx3Times/ns'][:]
        assert len(x2_trainIDs) == len(x2_timestamps), 'unmatching length'
        assert len(tpx3_triggerNrs) == len(tpx3_timestamps), 'unmatching length'
        assert len(set(x2_trainIDs)) == len(x2_trainIDs), 'found duplicates'
        assert len(set(x2_timestamps)) == len(x2_timestamps), 'found duplicates'
        start_index = find_nearest(x2_timestamps, tpx3_timestamps[0])
        assert not (missing_elements(x2_trainIDs[start_index:])), 'list of trainIDs is not continuous'
        trainIDs = [x2_trainIDs[start_index]]
        skip = 1
        for i in range(len(tpx3_triggerNrs) - 1):
            if (tpx3_timestamps[i + 1] - tpx3_timestamps[i]) > 15E7:
                skip += 1
            trainIDs.append(x2_trainIDs[start_index + i + skip])
        return (tpx3_triggerNrs, np.array(trainIDs))
