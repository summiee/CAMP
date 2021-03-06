import os
from pathlib import Path
import glob
from typing import NamedTuple
import numpy as np
import h5py
import yaml
import camp
from camp.utils.utils import find_nearest, check_for_completeness


class Ion:

    def __init__(self, fragments_config_file: str, fragment_name: str):
        experimental_set, fragment = fragment_name.split(',')
        print(experimental_set, fragment)
        with open(fragments_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        self.tof_start = cfg[experimental_set][fragment]['tof_start']
        self.tof_end = cfg[experimental_set][fragment]['tof_end']
        self.center_x = cfg[experimental_set][fragment]['center_x']
        self.center_y = cfg[experimental_set][fragment]['center_y']
        self.start_x = cfg[experimental_set][fragment]['start_x']
        self.end_x = cfg[experimental_set][fragment]['end_x']
        self.start_y = cfg[experimental_set][fragment]['start_y']
        self.end_y = cfg[experimental_set][fragment]['end_y']


class Filter(NamedTuple):
    '''filter for timepix_run.get_event method'''
    parameter: str
    start: float
    end: float


class TimePixRun:
    file_system = 'core'
    raw_datasets = ['x', 'y', 'tof', 'tot', 'trigger nr']
    centroided_datasets = ['x', 'y', 'tof', 'tot avg', 'tot max', 'clustersize', 'trigger nr']

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

    def get_hdf_dataset(self, hdf_dataset_name):
        with h5py.File(self.hdf_file, 'r') as h_file:
            values = h_file[str(hdf_dataset_name)][:]
        return values

    def get_events(self, event_type, parameters, *filter_parms, fragment=None):
        assert event_type in ('raw', 'centroided'), 'event type does not exist'
        if event_type == 'raw':
            assert all(elem in self.raw_datasets for elem in parameters), \
                'parameters do not exist in chosen event type'
        if event_type == 'centroided':
            assert all(elem in self.centroided_datasets for elem in parameters), \
                'parameters do not exist in chosen event type'
        if filter_parms and fragment:
            raise Exception('chosing filter parameters and fragments is too ambitious')

        timepix_dict = {}
        logical_map = None
        with h5py.File(self.hdf_file, 'r') as h_file:
            for parameter in parameters:
                timepix_dict[parameter] = h_file[str(str(event_type) + '/' + str(parameter))][:]

            if filter_parms:
                for filter_parm in filter_parms:
                    assert isinstance(filter_parm, Filter), \
                        'filter parameter is not instance of Filter obj'
                    if event_type == 'raw':
                        assert filter_parm.parameter in self.raw_datasets, \
                            'chosen filter parameter does not exist'
                    if event_type == 'centroided':
                        assert filter_parm.parameter in self.centroided_datasets, \
                            'chosen filter parameter does not exist'
                    assert type(filter_parm.start) in [int, float], \
                        'start value of filter is not a number'
                    assert type(filter_parm.end) in [int, float], \
                        'end value of filter is not a number'

                for filter_parm in filter_parms:
                    filter_parm_values = h_file[str(event_type) + '/' + str(filter_parm.parameter)][:]
                    logical_map_section = np.logical_and(filter_parm_values >= filter_parm.start,
                                                         filter_parm_values <= filter_parm.end)
                    if logical_map is None:
                        logical_map = logical_map_section
                    else:
                        logical_map = np.logical_and(logical_map, logical_map_section)

            if fragment is not None:
                fragment = Ion(self.fragments_config_file, fragment)
                x = h_file[str(event_type) + '/x'][:]
                y = h_file[str(event_type) + '/y'][:]
                tof = h_file[str(event_type) + '/tof'][:]
                x_logical_map = np.logical_and(x > fragment.start_x, x < fragment.end_x)
                y_logical_map = np.logical_and(y > fragment.start_y, y < fragment.end_y)
                tof_logical_map = np.logical_and(tof > fragment.tof_start, tof < fragment.tof_end)
                logical_map = np.logical_and.reduce((x_logical_map, y_logical_map, tof_logical_map))

        if logical_map is not None:
            for key in timepix_dict:
                timepix_dict[key] = timepix_dict[key][logical_map]

        return timepix_dict
