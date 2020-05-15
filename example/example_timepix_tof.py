from camp.timepix_run import TimePixRun
from camp.timepix_tof import Tof, TofvsPos1D, TofvsPos2D

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# extract data
timepix_dict = timepix_run.get_events('raw', ['tof', 'x'], fragment='fragments,test_ion')
tof, x = timepix_dict['tof'], timepix_dict['x']

# show ToF plots sequentially
Tof(tof)
TofvsPos1D(tof, x)
TofvsPos2D(tof, x)
