import os
import numpy as np
import h5py
import yaml
import camp.utils as cu
import camp.image_transform as cit
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class TimePixRun:
    file_system = 'core'
    config_data_path_file = '../config/beamtime.yaml'
    fragments_config_file = '../config/fragments.yaml'
    event_type = 'raw'

    def __init__(self, run_number: int):
        assert isinstance(run_number, int)
        self.run_number = run_number
        self.hdf_file = self.generate_hdf_filename()

    def generate_hdf_filename(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        timepix_hdf_path = cfg['path'][self.file_system] + cfg['timepix']
        try:
            file_start = "run_" + str(self.run_number).zfill(4)
            hdf_file = [i for i in os.listdir(timepix_hdf_path) if
                        os.path.isfile(os.path.join(timepix_hdf_path, i)) and i.startswith(
                            file_start) and not i.endswith(
                            'rawOnly.hdf5')][0]
            hdf_file_complete_path = timepix_hdf_path + hdf_file
            assert os.path.isfile(hdf_file_complete_path), 'File does not exist!'
            return hdf_file_complete_path
        except IndexError:
            print("Run", self.run_number, "does not exist!")

    def get_number_of_trains_from_hdf(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            self.number_of_trains = len(h_file['tpx3Times/triggerNr'][:])
        return self.number_of_trains

    def get_number_of_raw_events(self):
        tof, _, _ = self.get_tof_x_y()
        self.number_of_raw_events = tof.length
        return self.number_of_raw_events

    def get_pp_delay(self):
        with open(self.config_data_path_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        pp_delay_path = cfg['path'][self.file_system] + cfg['pp_delay']
        assert os.path.isfile(pp_delay_path), 'File does not exist!'
        try:
            with open(pp_delay_path, 'r') as ymlfile:
                yml = yaml.safe_load(ymlfile)
            self.pp_delay = yml['pp_delay'][self.run_number]
            return self.pp_delay
        except KeyError:
            print("Run", self.run_number, "does not have pump-probe delay.")
            return None

    def get_tof_x_y(self):
        with h5py.File(self.hdf_file, 'r') as h_file:
            tof = cu.trace(h_file[str(self.event_type) + '/tof'][:], label='ToF', unit='s')
            x_pos = cu.trace(h_file[str(self.event_type) + '/x'][:], label='x pos', unit='px')
            y_pos = cu.trace(h_file[str(self.event_type) + '/y'][:], label='y pos', unit='px')
        self.assert_equal_length([tof, x_pos, y_pos])
        return tof, x_pos, y_pos

    def indexed_array_by_tof(self, array, tof, tof_start, tof_end):
        return cu.trace(array.array[np.logical_and(tof.array > tof_start, tof.array < tof_end)],
                        label=array.label, unit=array.unit)

    def get_tof_x_y_sliced_by_tof(self, tof_start=0, tof_end=0.1):
        tof, x_pos, y_pos = self.get_tof_x_y()
        sliced_x_pos = self.indexed_array_by_tof(x_pos, tof, tof_start, tof_end)
        sliced_y_pos = self.indexed_array_by_tof(y_pos, tof, tof_start, tof_end)
        sliced_tof = self.indexed_array_by_tof(tof, tof, tof_start, tof_end)
        self.assert_equal_length([sliced_tof, sliced_x_pos, sliced_y_pos])
        return sliced_tof, sliced_x_pos, sliced_y_pos

    def get_tof_x_y_of_fragment(self, fragment_name):
        fragment = Ion(self.fragments_config_file, fragment_name)
        return self.get_tof_x_y_sliced_by_tof(fragment.tof_start, fragment.tof_end)

    def get_tof_x_y_of_trigger(self, trigger_nr):
        with h5py.File(self.hdf_file, 'r') as h_file:
            nr = h_file[str(self.event_type) + '/nr'][:]
            tof = cu.trace(h_file[str(self.event_type) + '/tof'][nr == trigger_nr], label='ToF', unit='s')
            x_pos = cu.trace(h_file[str(self.event_type) + '/x'][nr == trigger_nr], label='x pos', unit='px')
            y_pos = cu.trace(h_file[str(self.event_type) + '/y'][nr == trigger_nr], label='y pos', unit='px')
        self.assert_equal_length([tof, x_pos, y_pos])
        return tof, x_pos, y_pos

    def display_tof_and_vmi_of_tof_interval(self, tof_start=0, tof_end=0.1, time_unit='micro'):
        tof, x_pos, y_pos = self.get_tof_x_y_sliced_by_tof(tof_start, tof_end)
        cu.MultiplePlots(PlotTof(tof, time_unit=time_unit), VmiImage(x_pos, y_pos))

    def display_tof_and_vmi_of_fragment(self, fragment_name, time_unit='micro'):
        tof, x_pos, y_pos = self.get_tof_x_y_of_fragment(fragment_name)
        cu.MultiplePlots(PlotTof(tof, time_unit=time_unit), VmiImage(x_pos, y_pos))

    def display_tof_and_vmi_of_trigger(self, trigger_nr, time_unit='micro'):
        tof, x_pos, y_pos = self.get_tof_x_y_of_trigger(trigger_nr)
        cu.MultiplePlots(PlotTof(tof, time_unit=time_unit), VmiImage(x_pos, y_pos))

    def assert_equal_length(self, list_of_obj):
        for i in range(len(list_of_obj) - 1):
            assert list_of_obj[0].length == list_of_obj[i + 1].length


class Ion:

    def __init__(self, fragments_config_file: str, fragment_name: str):
        with open(fragments_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        self.tof_start = cfg['fragments'][fragment_name]['tof_start']
        self.tof_end = cfg['fragments'][fragment_name]['tof_end']
        self.center_x = cfg['fragments'][fragment_name]['center_x']
        self.center_y = cfg['fragments'][fragment_name]['center_y']


class TimeAxis:

    def __init__(self, trace, new_unit):
        self.length = trace.length
        self.label = trace.label
        self.time_transformation(trace.array, new_unit)

    def time_transformation(self, time_axis_in_seconds, new_time_unit):
        units = [None, 'milli', 'micro', 'nano']
        factors = [1, 10 ** 3, 10 ** 6, 10 ** 9]
        plot_units = ['s', 'ms', '\u03BCs', 'ns']
        index = int(np.array([i for i in range(len(units)) if units[i] == new_time_unit]))
        self.array = time_axis_in_seconds * factors[index]
        self.unit = new_time_unit
        self.plot_unit = plot_units[index]


class PlotTof(cu.LinePlot):
    bins = 100
    title = 'histogram: time-of-flight'
    ylabel = 'number of events'

    def __init__(self, tof, time_unit='micro'):
        self.tof = tof
        self.time_unit = time_unit
        time_axis = TimeAxis(self.tof, self.time_unit)
        self.xlabel = 'ToF [{}]'.format(time_axis.plot_unit)
        self.x, self.y = self.hist_to_xy(time_axis.array, self.bins)


class PlotTofvsPos1D(cu.ScatterPlot):

    def __init__(self, tof, dim, time_unit='micro'):
        self.time_unit = time_unit
        time_axis = TimeAxis(tof, self.time_unit)
        self.x = time_axis.array
        self.y = dim.array
        self.title = tof.label + '  vs  ' + dim.label
        self.xlabel = 'ToF [{}]'.format(time_axis.plot_unit)
        self.ylabel = '{} [{}]'.format(dim.label, dim.unit)


class PlotTofvsPos2D(cu.Hist2D):
    bin_tof = 6000
    bin_space = 256

    def __init__(self, tof, dim, time_unit='micro'):
        self.time_unit = time_unit
        time_axis = TimeAxis(tof, self.time_unit)
        self.x = time_axis.array
        self.y = dim.array
        self.bins = (self.bin_tof, np.linspace(0, self.bin_space, self.bin_space + 1))
        self.title = tof.label + '  vs  ' + dim.label
        self.xlabel = 'ToF [{}]'.format(time_axis.plot_unit)
        self.ylabel = '{} [{}]'.format(dim.label, dim.unit)


class VmiImage(cu.Hist2D):
    bin_space = 256  # number of pixel

    def __init__(self, x, y):
        self.x = x.array
        self.y = y.array
        self.bins = np.linspace(0, self.bin_space, self.bin_space + 1)
        self.title = 'VMI image'
        self.xlabel = '{} [{}]'.format(x.label, x.unit)
        self.ylabel = '{} [{}]'.format(y.label, y.unit)

    def create_image(self):
        """Rotate to keep same orientation as plt.hist2d from method: show() """
        counts, xbins, ybins = np.histogram2d(self.x, self.y, bins=(self.bins, self.bins))
        return np.rot90(counts)

    def show(self):
        plt.imshow(self.create_image())
        plt.show()

    def zoom_in(self, start_point, end_point):
        x_start, y_start = start_point
        x_end, y_end = end_point
        image = self.create_image()
        plt.imshow(image[y_start: y_end, x_start:x_end], extent=[x_start, x_end, y_end, y_start])
        plt.show()

    def create_cart_image(self, image, center, angles=None, radii=None):
        fig = plt.figure()
        plt.imshow(image)
        plt.plot(center[0], center[1], 'ro')
        plt.xlabel('x_pos [px]')
        plt.ylabel('y_pos [px]')
        plt.title('VMI image')
        if angles or radii:
            if not angles:
                angles = (0, 360)
            if not radii:
                radii = (0, 1000)
                # patches have diff coordinates and direction
            plt.gcf().gca().add_patch(
                patches.Wedge((center[0], center[1]), radii[1], (270 - angles[1]), (270 - angles[0]),
                              color="r", alpha=0.2, width=radii[1] - radii[0]))

    def create_polar_image(self, image_polar, angles=None, radii=None):
        fig = plt.figure()
        plt.imshow(image_polar)
        plt.xlabel('angle [°]')
        plt.ylabel('radius [px]')
        plt.title('polar coordinates')
        if angles or radii:
            if not angles:
                size = (0, image_polar.shape[1])
            if not radii:
                radii = (0, image_polar.shape[0])
            origin = (angles[0], radii[0])
            height = radii[1] - radii[0]
            if angles[0] < 0:
                origin2 = (360 + angles[0], radii[0])
                plt.gcf().gca().add_patch(patches.Rectangle(origin2, -angles[0], height, color='r', alpha=0.2))
                angles = (0, angles[1])
            size = angles[1] - angles[0]
            origin = (angles[0], radii[0])
            plt.gcf().gca().add_patch(patches.Rectangle(origin, size, height, color='r', alpha=0.2))

    def extract_profileline(self, image_polar, angles=None, radii=None):
        if not angles:
            angles = (0, image_polar.shape[1])
        if not radii:
            radii = (0, image_polar.shape[0])
        if angles[0] >= 0:
            radial_average = np.average(image_polar[radii[0]:radii[1], angles[0]:angles[1]], axis=1)
        else:
            radial_average_1 = np.average(image_polar[radii[0]:radii[1], 0:angles[1]], axis=1)
            radial_average_2 = np.average(image_polar[radii[0]:radii[1], angles[0]:-1], axis=1)
            radial_average = np.average(np.array([radial_average_1, radial_average_2]),
                                        axis=0, weights=np.array([angles[1], -angles[0]]))
        pixel_from_center = np.arange(radii[0], radii[1])
        assert len(pixel_from_center) == len(radial_average)
        return (pixel_from_center, radial_average)

    def plot_profileline(self, radial_average):
        fig = plt.figure()
        plt.plot(radial_average[0], radial_average[1])
        plt.xlabel('radius [px]')
        plt.ylabel('profile line [a.u.]')
        plt.title('radial average')

    def create_radial_average(self, center, angles=None, radii=None):
        image = self.create_image()
        self.create_cart_image(image, center, angles, radii)
        image_polar, _, _ = cit.reproject_image_into_polar(image, origin=center, dt=np.pi / 180)
        self.create_polar_image(image_polar, angles, radii)
        radial_average = self.extract_profileline(image_polar, angles, radii)
        self.plot_profileline(radial_average)
        plt.show()
        return radial_average
