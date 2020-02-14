from beamtimedaqaccess import BeamtimeDaqAccess
import camp.bda_utils as cbu
import matplotlib.pyplot as plt

root_dir = '/asap3/flash/gpfs/bl1/2019/data/11006902/raw/hdf/online-0/'

daq = BeamtimeDaqAccess.create(root_dir)

run_number = 32474

def show_average_trace_of_run(daq, run_number):
    ghz_adc_addr = '/FL1/Experiment/BL1/ADQ412 GHz ADC/CH00/TD'
    average_adc_trace = cbu.total_adc_average_of_run(daq, ghz_adc_addr, run_number)
    plt.plot(average_adc_trace)
    plt.show()


def show_average_image_of_run(daq, run_number):
    cmos_addr = '/FL1/Experiment/BL1/CAMP/VMI CMOS camera 1/image'
    average_image = cbu.average_image_of_run(daq, cmos_addr, run_number)
    plt.imshow(average_image)
    plt.show()


help(cbu)
