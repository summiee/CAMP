from beamtimedaqaccess import BeamtimeDaqAccess
from camp.bda_utils.bda_utils import average_adc_of_run, average_image_of_run
import matplotlib.pyplot as plt

root_dir = '/asap3/flash/gpfs/bl1/2019/data/11006902/raw/hdf/online-0/'

daq = BeamtimeDaqAccess.create(root_dir)

run_number = 32474


def show_average_trace_of_run(daq, run_number):
    ghz_adc_addr = '/FL1/Experiment/BL1/ADQ412 GHz ADC/CH00/TD'
    average_adc_trace = average_adc_of_run(daq, ghz_adc_addr, run_number)
    plt.plot(average_adc_trace)
    plt.show()


def show_average_image_of_run(daq, run_number):
    cmos_addr = '/FL1/Experiment/BL1/CAMP/VMI CMOS camera 1/image'
    average_image = average_image_of_run(daq, cmos_addr, run_number)
    plt.imshow(average_image)
    plt.show()


show_average_trace_of_run(daq, run_number)
# show_average_image_of_run(daq, run_number)
