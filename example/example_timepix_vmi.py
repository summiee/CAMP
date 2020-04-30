from camp.timepix_run import TimePixRun
from camp.timepix_vmi import VmiImage

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# extract data
x_pos, y_pos, tof, tot_avg, tot_max, clustersize, trigger_nr = timepix_run.get_centroided_events_of_fragment('test_ion')

# show VMI image
vmi_image = VmiImage(x_pos, y_pos)
vmi_image.show()

# zoom in VMI image
x_start, x_end = 120, 130
y_start, y_end = 60, 70
vmi_image.zoom_in(x_start, x_end, y_start, y_end)

# radial averaging
x_center, y_center = 130, 110

## optional for circle/ ring sectors
start_angle, end_angle = -45, 45  # degrees
start_radius, end_radius = 20, 100  # pixel

radial_average = VmiImage(x_pos, y_pos).create_radial_average((x_center, y_center), angles=(start_angle, end_angle),
                                                              radii=(start_radius, end_radius))
