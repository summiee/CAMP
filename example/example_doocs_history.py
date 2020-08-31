from camp.pydoocs_utils.pydoocs_utils import DoocsHistory
import matplotlib.pyplot as plt

doocs_hist_addr = 'FLASH.FEL/BL.PRESSURE/BL1.3/SENSOR1.PRESSURE.HIST'
start_time = "2018-11-20 16:00:00"
stop_time = "2018-11-21 16:00:00"

history = DoocsHistory(doocs_hist_addr)
times, pressures = history.get_doocs_history(start_time, stop_time)

plt.plot(times, pressures)
plt.show()
