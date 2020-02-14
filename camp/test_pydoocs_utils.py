import unittest
import camp.pydoocs_utils as cpu


class TestPydoocsUtils(unittest.TestCase):

    def test_pydoocs_version(self):
        from pydoocs import __version__
        self.assertGreaterEqual(__version__, '2.0.4')

    def test_get_current_trainID(self):
        self.assertEqual(type(cpu.get_current_train_id()), int)


class TestDoocsHistory(unittest.TestCase):

    def test_time_to_timestamp(self):
        self.assertEqual(cpu.DoocsHistory('FLASH.FEL/BL.PRESSURE/BL1.3/SENSOR1.PRESSURE.HIST').time_to_timestamp(
            '2018-11-20 16:00:00'), 1542726000)
        self.assertNotEqual(cpu.DoocsHistory('FLASH.FEL/BL.PRESSURE/BL1.3/SENSOR1.PRESSURE.HIST').time_to_timestamp(
            '2018-11-20 16:00:00'), 1542726001)

    def test_read_doocs_hist(self):
        doocs_hist_addr = 'FLASH.FEL/BL.PRESSURE/BL1.3/SENSOR1.PRESSURE.HIST'
        start_time = "2018-11-20 16:00:00"
        stop_time = "2018-11-21 16:00:00"
        times, pressures = cpu.DoocsHistory(doocs_hist_addr).get_doocs_history(start_time, stop_time)
        self.assertEqual(len(times), len(pressures))
        self.assertGreaterEqual(len(times), 0)


if __name__ == '__main__':
    unittest.main()
