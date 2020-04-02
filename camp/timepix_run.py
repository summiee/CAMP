import os
import camp
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

    def __init__(self, run_number: int, event_type='raw'):
        assert isinstance(run_number, int)
        self.run_number = run_number
        self.event_type = event_type
        self.__generate_config_file_path()
        self.__generate_hdf_filename()

    def __generate_config_file_path(self):
        self.config_data_path_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/beamtime.yaml'))
        self.fragments_config_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/fragments.yaml'))
        self.run_number_config_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/run_numbers.yaml'))

    def __generate_hdf_filename(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        timepix_hdf_path = cfg['path'][self.file_system] + cfg['timepix']
        try:
            file_start = "run_" + str(self.run_number).zfill(4)
            hdf_file = [i for i in os.listdir(timepix_hdf_path) if
                        os.path.isfile(os.path.join(timepix_hdf_path, i)) and i.startswith(
                            file_start) and i.endswith('.hdf5') and i[-6].isdigit() == True][0]
            hdf_file_complete_path = timepix_hdf_path + hdf_file
            assert os.path.isfile(hdf_file_complete_path), 'File does not exist!'
            self.hdf_file = hdf_file_complete_path
        except IndexError:
            print("Run", self.run_number, "does not exist!")

    def get_number_of_trains_from_hdf(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            self.number_of_trains = len(h_file['timing/timepix/triggerNr'][:])
        return self.number_of_trains

    def get_number_of_raw_events(self):
        tof, _, _ = self.get_tof_x_y()
        self.number_of_raw_events = tof.length
        return self.number_of_raw_events

    def get_pp_delay(self):
        """
        Obsolte when synchronized with FLASH DAQ
        """
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

    def get_flash_run_number(self):
        try:
            with open(self.run_number_config_file, 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)
            self.flash_run_number = cfg[self.run_number]
            return self.flash_run_number
        except KeyError:
            print("Run", self.run_number, "does not have a corresponding FLASH DAQ run number.")
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
            nr = h_file[str(self.event_type) + '/triggerNumber'][:]
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
            x2_trainIDs = h_file['timing/facility/trainID'][:]
            x2_timestamps = h_file['timing/facility/timestamp'][:]
            tpx3_triggerNrs = h_file['timing/timepix/triggerNr'][:]
            tpx3_timestamps = h_file['timing/timepix/timestamp'][:]
        assert len(x2_trainIDs) == len(x2_timestamps), 'unmatching length'
        assert len(tpx3_triggerNrs) == len(tpx3_timestamps), 'unmatching length'
        assert len(np.unique(x2_trainIDs)) == len(x2_trainIDs), 'found duplicates'
        assert len(np.unique(x2_timestamps)) == len(x2_timestamps), 'found duplicates'
        assert len(np.unique(tpx3_triggerNrs)) == len(tpx3_triggerNrs), 'found duplicates'
        assert len(np.unique(tpx3_timestamps)) == len(tpx3_timestamps), 'found duplicates'
        start_index = find_nearest(x2_timestamps, tpx3_timestamps[0])
        assert not (missing_elements(x2_trainIDs[start_index:])), 'list of trainIDs is not continuous'
        trainIDs = [x2_trainIDs[start_index]]
        trigger_Nrs = [tpx3_triggerNrs[0]]
        skip = 1
        for i in range(len(tpx3_triggerNrs) - 1):
            if (tpx3_triggerNrs[i + 1] - tpx3_triggerNrs[i]) == 2:
                skip += 1
            try:
                trainIDs.append(x2_trainIDs[start_index + i + skip])
                trigger_Nrs.append(tpx3_triggerNrs[i + 1])
            except IndexError:
                pass
        assert len(trainIDs) == len(trigger_Nrs), 'matching fails'
        return (np.array(trigger_Nrs), np.array(trainIDs))

    def get_clustersizes(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            clustersizes = trace(h_file['centroided/clustersize'][:])
        return clustersizes

    def get_clustersizes_sliced_by_tof_interval(self, tof_start=0, tof_end=0.1):
        clustersizes = self.get_clustersizes()
        tof, _, _ = self.get_tof_x_y()
        sliced_clustersizes = self.__slice_by_tof(clustersizes, tof, tof_start, tof_end)
        return sliced_clustersizes

    def get_clustersizes_of_fragment(self, fragment_name):
        fragment = Ion(self.fragments_config_file, fragment_name)
        return self.get_clustersizes_sliced_by_tof_interval(fragment.tof_start, fragment.tof_end)
