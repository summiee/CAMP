from camp.timepix_utils import *

run_number = 178  # short run
timepix_run = TimePixRun(run_number)
fragment = 'test_ion'

tof, x_pos, y_pos = timepix_run.get_tof_x_y_of_fragment(fragment)

x_center, y_center = 130, 110

# optional for circle/ ring sectors
start_angle, end_angle = -45, 45  # degrees
start_radius, end_radius = 20, 100  # pixel

radial_average = VmiImage(x_pos, y_pos).create_radial_average((x_center, y_center), angles=(start_angle, end_angle),
                                                              radii=(start_radius, end_radius))
