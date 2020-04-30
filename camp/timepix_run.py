import os
import camp
from pathlib import Path
import glob
import numpy as np
import h5py
import yaml
from camp.utils import find_nearest, check_for_completeness


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

    def __init__(self, run_number: int):
        assert isinstance(run_number, int)
        self.run_number = run_number
        self.__generate_config_file_path()
        self.__generate_hdf_filename()
        self.__fetch_attributes()

    def __generate_config_file_path(self):
        self.config_data_path_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/beamtime.yaml'))
        self.fragments_config_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/fragments.yaml'))
        self.run_number_config_file = Path(os.path.join(os.path.dirname(camp.__file__), '../config/run_numbers.yaml'))

    def __generate_hdf_filename(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        timepix_hdf_path = cfg['path'][self.file_system] + cfg['timepix']
        try:
            file_list = glob.glob(f'{timepix_hdf_path}run_{self.run_number:04d}_*.hdf5')
            assert len(file_list) < 2, f' assignment ambiguous - more than 1 hdf_file for: {self.run_number}'
            self.hdf_file = Path(file_list[0])
        except IndexError:
            print("Run", self.run_number, "not found!")

    def __fetch_attributes(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            self.recorded_trigger = h_file['timing/timepix/'].attrs.__getitem__('nr events')
            self.recorded_trainIDs = h_file['timing/facility/'].attrs.__getitem__('nr events')
            self.number_of_raw_events = h_file['raw/'].attrs.__getitem__('nr events')
            self.number_of_centroided_events = h_file['centroided/'].attrs.__getitem__('nr events')
            self.trainID_shift = h_file['timing/facility/'].attrs.__getitem__('shift')
            self.corr_coeff = h_file['timing/facility/'].attrs.__getitem__('corr coeff')

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

    def get_raw_events(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            x_pos = trace(h_file['raw/x'][:], label='x pos', unit='px')
            y_pos = trace(h_file['raw/y'][:], label='y pos', unit='px')
            tof = trace(h_file['raw/tof'][:], label='ToF', unit='s')
            tot = trace(h_file['raw/tot'][:], label='ToT', unit='s')
            trigger_nr = trace(h_file['raw/trigger nr'][:], label='trigger', unit='')
        self.__assert_equal_length([x_pos, y_pos, tof, tot, trigger_nr])
        return x_pos, y_pos, tof, tot, trigger_nr

    def get_raw_events_by_tof_interval(self, tof_start=0, tof_end=0.1):
        x_pos, y_pos, tof, tot, trigger_nr = self.get_raw_events()
        sliced_x_pos = self.__slice_by_tof(x_pos, tof, tof_start, tof_end)
        sliced_y_pos = self.__slice_by_tof(y_pos, tof, tof_start, tof_end)
        sliced_tot = self.__slice_by_tof(tot, tof, tof_start, tof_end)
        sliced_trigger_nr = self.__slice_by_tof(trigger_nr, tof, tof_start, tof_end)
        sliced_tof = self.__slice_by_tof(tof, tof, tof_start, tof_end)
        self.__assert_equal_length([sliced_x_pos, sliced_y_pos, sliced_tof, sliced_tot, sliced_trigger_nr])
        return sliced_x_pos, sliced_y_pos, sliced_tof, sliced_tot, sliced_trigger_nr

    def get_raw_events_of_fragment(self, fragment_name):
        fragment = Ion(self.fragments_config_file, fragment_name)
        return self.get_raw_events_by_tof_interval(fragment.tof_start, fragment.tof_end)

    def get_centroided_events(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            x_pos = trace(h_file['centroided/x'][:], label='x pos', unit='px')
            y_pos = trace(h_file['centroided/y'][:], label='y pos', unit='px')
            tof = trace(h_file['centroided/tof'][:], label='ToF', unit='s')
            tot_avg = trace(h_file['centroided/tot avg'][:], label='ToT avg', unit='s')
            tot_max = trace(h_file['centroided/tot max'][:], label='ToT max', unit='s')
            clustersize = trace(h_file['centroided/clustersize'][:], label='clustersize', unit='')
            trigger_nr = trace(h_file['centroided/trigger nr'][:], label='trigger', unit='')
        self.__assert_equal_length([x_pos, y_pos, tof, tot_avg, tot_max, clustersize, trigger_nr])
        return x_pos, y_pos, tof, tot_avg, tot_max, clustersize, trigger_nr

    def get_centroided_events_by_tof_interval(self, tof_start=0, tof_end=0.1):
        x_pos, y_pos, tof, tot_avg, tot_max, clustersize, trigger_nr = self.get_centroided_events()
        sliced_x_pos = self.__slice_by_tof(x_pos, tof, tof_start, tof_end)
        sliced_y_pos = self.__slice_by_tof(y_pos, tof, tof_start, tof_end)
        sliced_tot_avg = self.__slice_by_tof(tot_avg, tof, tof_start, tof_end)
        sliced_tot_max = self.__slice_by_tof(tot_max, tof, tof_start, tof_end)
        sliced_clustersize = self.__slice_by_tof(clustersize, tof, tof_start, tof_end)
        sliced_trigger_nr = self.__slice_by_tof(trigger_nr, tof, tof_start, tof_end)
        sliced_tof = self.__slice_by_tof(tof, tof, tof_start, tof_end)
        self.__assert_equal_length(
            [sliced_x_pos, sliced_y_pos, sliced_tof, sliced_tot_avg, sliced_tot_max, sliced_clustersize,
             sliced_trigger_nr])
        return sliced_x_pos, sliced_y_pos, sliced_tof, sliced_tot_avg, sliced_tot_max, sliced_clustersize, sliced_trigger_nr

    def get_centroided_events_of_fragment(self, fragment_name):
        fragment = Ion(self.fragments_config_file, fragment_name)
        return self.get_centroided_events_by_tof_interval(fragment.tof_start, fragment.tof_end)

    def __slice_by_tof(self, array, tof, tof_start, tof_end):
        return trace(array.array[np.logical_and(tof.array > tof_start, tof.array < tof_end)],
                     label=array.label, unit=array.unit)

    def __assert_equal_length(self, list_of_obj):
        for i in range(len(list_of_obj) - 1):
            assert list_of_obj[0].length == list_of_obj[i + 1].length

    def get_trainIDs(self, shifted=True):
        with h5py.File(self.hdf_file, 'r') as h_file:
            x2_trainIDs = h_file['timing/facility/train id'][:]
            x2_timestamps = h_file['timing/facility/timestamp'][:]
            tpx3_triggerNrs = h_file['timing/timepix/trigger nr'][:]
            tpx3_timestamps = h_file['timing/timepix/timestamp'][:]
        assert len(x2_trainIDs) == len(x2_timestamps), 'unmatching length'
        assert len(tpx3_triggerNrs) == len(tpx3_timestamps), 'unmatching length'
        assert len(np.unique(x2_trainIDs)) == len(x2_trainIDs), 'found duplicates'
        assert len(np.unique(x2_timestamps)) == len(x2_timestamps), 'found duplicates'
        assert len(np.unique(tpx3_triggerNrs)) == len(tpx3_triggerNrs), 'found duplicates'
        assert len(np.unique(tpx3_timestamps)) == len(tpx3_timestamps), 'found duplicates'
        start_index = find_nearest(x2_timestamps, tpx3_timestamps[0])
        assert not (check_for_completeness(x2_trainIDs[start_index:])), 'list of trainIDs is not continuous'
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
        trigger_Nrs, trainIDs = np.array(trigger_Nrs), np.array(trainIDs)
        if shifted == True and ~np.isnan(self.trainID_shift):
            trainIDs = trainIDs + self.trainID_shift
        return trigger_Nrs, trainIDs
