from camp.timepix.run import TimePixRun
from camp.timepix.vmi import VmiImage

run_number = 178  # short run
timepix_run = TimePixRun(run_number)

# extract data
timepix_dict = timepix_run.get_events('centroided', ['x', 'y'], fragment='fragments,test_ion')
x, y = timepix_dict['x'], timepix_dict['y']

# show VMI image
vmi_image = VmiImage(x, y)
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

radial_average = VmiImage(x, y).create_radial_average((x_center, y_center), angles=(start_angle, end_angle),
                                                      radii=(start_radius, end_radius))
