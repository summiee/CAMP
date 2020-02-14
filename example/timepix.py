from camp.timepix_utils import *

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# print all methods and attributes of timepix_run object
help(timepix_run)

# example usage 1
tof, x_pos, y_pos = timepix_run.get_tof_x_y_of_fragment('test_ion')
VmiImage(x_pos, y_pos).show()

# example usage 2
tof_start = 7.8E-6
tof_end = 8.6E-6
timepix_run.display_tof_and_vmi_of_tof_interval(tof_start, tof_end)

# example usage 3
trigger_nr = 0
tof, x_pos, y_pos = timepix_run.get_tof_x_y_of_trigger(trigger_nr)
print(f'Events found for trigger number {trigger_nr}: {tof.length}')
