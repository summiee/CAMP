import collections
import pydoocs
import numpy as np
from datetime import datetime
import time
from typing import Tuple
import re
import os.path
import h5py


def get_current_train_id() -> int:
    """Returns current train_ID from reliable source"""
    train_id = int(pydoocs.read('FLASH.FEL/TIMER/EXP2/MACRO_PULSE_NUMBER')['data'])
    return train_id


class TrainAbo:

    def __init__(self, doocs_addr: str):
        self.doocs_addr = doocs_addr
        self.train_id = 0

    def channel_keys(self) -> collections.abc.KeysView:
        pydoocs_dict = pydoocs.read(self.doocs_addr)
        assert isinstance(pydoocs_dict, dict)
        return pydoocs_dict.keys()

    def trains(self, number_of_trains: int) -> dict:
        """ Retruns *number_of_trains* unique trains as generator
         *number_of_trains* = -1 will loop indefinitely"""
        number_of_passed_train = 0
        while (number_of_passed_train < number_of_trains) or number_of_trains == -1:
            pydoocs_dict = pydoocs.read(self.doocs_addr)
            self.assert_pydoocs_dict()
            current_id = pydoocs_dict['macropulse']
            assert current_id != 0, '{} returns trainID: 0'.format(self.doocs_addr)
            if self.train_id != current_id:
                self.train_id = current_id
                yield pydoocs_dict
                number_of_passed_train += 1
            else:
                time.sleep(0.01)

    def to_hdf(self, filename: str, key_list: list, number_of_trains: int) -> None:
        self.assert_to_hdf(filename, key_list, number_of_trains)
        pydoocs_dict = pydoocs.read(self.doocs_addr)
        self.assert_pydoocs_dict(key_list)
        number_of_passed_train = 0
        dset = {}
        with h5py.File(filename, "w") as f:
            for key in key_list:
                if type(pydoocs_dict[key]) in [int, float]:
                    dset[key] = f.create_dataset(key, (number_of_trains,), dtype=np.dtype(type(pydoocs_dict[key])))
                if isinstance(pydoocs_dict[key], np.ndarray):
                    dset[key] = f.create_dataset(key, (
                        number_of_trains, pydoocs_dict[key].shape[0], pydoocs_dict[key].shape[1]))
                if isinstance(pydoocs_dict[key], str):
                    key_list.remove(key)
                    f.attrs[key] = pydoocs_dict[key]
                    print('The following key is a string and therefore appended as file.attribute: {}'.format(key))
            for channel in self.trains(number_of_trains):
                for key in key_list:
                    try:
                        dset[key][number_of_passed_train] = channel[key]
                    except:
                        pass
                number_of_passed_train += 1
        print('Done - Writing {} trains to HDF5.'.format(number_of_trains))

    def assert_pydoocs_dict(self, key_list=None) -> None:
        pydoocs_dict = pydoocs.read(self.doocs_addr)
        if not key_list:
            key_list = ["data", "macropulse"]
        for key in key_list:
            assert key in pydoocs_dict, '{} is missing in pydoocs dict'.format(key)

    def assert_to_hdf(self, filename: str, key_list: list, number_of_trains: int) -> None:
        assert isinstance(filename, str)
        assert os.path.isfile(filename) != True, 'file already exist'
        assert isinstance(number_of_trains, int)
        assert number_of_trains > 0
        assert isinstance(key_list, list)
        assert len(key_list) != 0
        self.assert_pydoocs_dict(key_list)


class TrainFile:

    def __init__(self, filename: str):
        self._h5file = None
        self._filename = filename

    def __enter__(self):
        self.assert_to_hdf()
        self._h5file = h5py.File(self._filename, 'r')
        return self

    def __exit__(self, type, value, traceback):
        self._h5file.close()

    def contains(self):
        print(f'Groups: {list(self._h5file.keys())}')
        print(f'Attibutes: {list(self._h5file.attrs.keys())}')
        if self._h5file['macropulse']:
            print('Number of trains in file: {}'.format(len(self._h5file['macropulse'])))

    def get_channel_data(self, key):
        try:
            return self._h5file[key][()]
        except KeyError:
            print('{} is not included in {}'.format(key, self._filename))

    def assert_to_hdf(self) -> None:
        assert isinstance(self._filename, str)
        assert os.path.isfile(self._filename) == True, 'file do not exists'


class DoocsHistory:

    def __init__(self, doocs_addr: str):
        assert doocs_addr.endswith('.HIST'), 'no valid DOOCS history address'
        self.doocs_addr = doocs_addr

    def time_to_timestamp(self, time: str):
        """Transforms time_string to timestamp"""
        return datetime.timestamp(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))

    def get_doocs_history(self, start_time: str, stop_time: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns a np.array of datetime objects and a np.array
        of DOOCS values ['data'] from the DOOOCS history for
        a given time interval
        """
        self.assert_time_string([start_time, stop_time])
        self.start_time = self.time_to_timestamp(start_time)
        self.stop_time = self.time_to_timestamp(stop_time)
        pydoocs_dict = pydoocs.read(self.doocs_addr, parameters=[self.start_time, self.stop_time, 256, 0])
        self.assert_pydoocs_dict(pydoocs_dict)
        timestamps = np.array(pydoocs_dict["data"])[:, 0]
        values = np.array(pydoocs_dict["data"])[:, 1]
        times = np.array([datetime.fromtimestamp(timestamp) for timestamp in timestamps])
        self.assert_return_values(times, values)
        return times, values

    def assert_time_string(start_time, times):
        for time in times:
            assert isinstance(time, str), "time have to be str"
            assert bool(time) == True, "time can not be empty"
            assert re.match('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d',
                            time), 'date pattern must have form: 2018-11-20 16:00:00'

    def assert_pydoocs_dict(self, pydoocs_dict):
        assert isinstance(pydoocs_dict, dict)
        assert 'data' in pydoocs_dict
        assert isinstance(pydoocs_dict['data'], list)

    def assert_return_values(self, times, values):
        assert isinstance(times, np.ndarray)
        assert len(times) != 0
        assert isinstance(times[0], datetime)
        assert len(times) == len(values)


def get_current_trainID():
    return None
