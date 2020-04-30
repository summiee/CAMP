from camp.timepix_run import TimePixRun
from camp.timepix_tof import Tof, TofvsPos1D, TofvsPos2D

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# extract data
x_pos, y_pos, tof, tot, trigger_nr = timepix_run.get_raw_events_of_fragment('test_ion')

# show ToF plots sequentially
Tof(tof)
TofvsPos1D(tof, x_pos)
TofvsPos2D(tof, x_pos)
