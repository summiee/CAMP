from camp.timepix_run import TimePixRun
from camp.timepix_tof import Tof, TofvsPos1D, TofvsPos2D

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# extract data
tof, x_pos, y_pos = timepix_run.get_tof_x_y_of_fragment('test_ion')

# show ToF plots sequentially
Tof(tof)
TofvsPos1D(tof, x_pos)
TofvsPos2D(tof, x_pos)