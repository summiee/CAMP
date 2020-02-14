import unittest
from hamcrest import *
import camp.pydoocs_utils as cpu
import os


class TestIntegrationPydoocsUtils(unittest.TestCase):

    def setUp(self) -> None:
        doocs_addr = 'FLASH.FEL/ADC.SIS.BL1/EXP1.CH00/CH00.TD'
        self.train_abo = cpu.TrainAbo(doocs_addr)

    def test_train_abo_has_channel_keys(self):
        assert_that(self.train_abo.channel_keys(), has_items('data', 'timestamp', 'macropulse'))

    def test_train_abo_generates_channels_with_increasing_train_ids(self):
        # When
        train_ids = [each['macropulse'] for each in self.train_abo.trains(3)]
        # Then
        train_id_increments = [a - b for a, b in zip(train_ids[1:], train_ids[:-1])]
        assert_that(train_id_increments, only_contains(greater_than(0)))

    def test_train_abo_writes_hdf(self):
        # Given
        key_list = ['data', 'timestamp', 'macropulse']
        number_of_trains = 5
        filename = 'data/test.h5'
        if os.path.isfile(filename):
            os.remove(filename)
        # When
        self.train_abo.to_hdf(filename, key_list, number_of_trains)
        # Then
        assert_that(os.path.isfile(filename))
        # TODO add more assertion about file contents
