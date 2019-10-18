import pydoocs
import numpy as np
import time

number_of_pulse_trains_to_average = 10

adc_doocs_address = 'FLASH.FEL/ADC.ADQ.BL1/EXP1.CH00/CH00.DAQ.TD'

def wait_for_next_train():
    seconds_between_trains = 0.1       # 10Hz FLASH repetion rate
    time.sleep(seconds_between_trains)

def time_value_matrix_waiting(adc_address):
    wait_for_next_train()
    adc_dictonary = pydoocs.read(adc_address)
    time_value_matrix = adc_dictonary['data']
    return time_value_matrix

time_value_matrices = [time_value_matrix_waiting(adc_doocs_address) for each_train in range(number_of_pulse_trains_to_average)]
adc_traces = [each_matrix[:,1] for each_matrix in time_value_matrices]
adc_trace_average = np.average(adc_traces, axis=0)
np.save('average_tof', adc_trace_average)

print('Done taking ADC traces')


