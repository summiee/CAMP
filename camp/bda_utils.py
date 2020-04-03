import numpy as np
import h5py
import glob


def section_ID_intervals(total_interval, section_length):
    assert isinstance(total_interval, tuple)
    assert len(total_interval) == 2
    assert total_interval[0] <= total_interval[1]
    assert isinstance(section_length, int)
    assert section_length > 0
    sections = [(start, start + section_length) for start in
                range(total_interval[0], total_interval[1], section_length)]
    sections[-1] = (sections[-1][0], total_interval[1])  # fix last section
    return sections


def weight_and_adc_average_of_section(daq, adc_addr, section):
    traces = daq.valuesOfInterval(adc_addr, section)
    checked_traces = np.array([trace for trace in traces if np.sum(trace) != 0 or True])  # check for empty/NaN traces
    average_trace = np.average(checked_traces, axis=0)
    weight = checked_traces.shape[0]
    return average_trace, weight


def total_adc_average_of_run(daq, adc_addr, run_number):
    total_trainID_inteval = daq.pulseIdIntervalOfRun(adc_addr, run_number)
    section_length = 1000
    sections = section_ID_intervals(total_trainID_inteval, section_length)
    list_comp = np.array([weight_and_adc_average_of_section(daq, adc_addr, section) for section in sections])
    trace = np.average(list_comp[:, 0], axis=0, weights=list_comp[:, 1])
    return trace


def average_image_and_weight_of_section(daq, cam_addr, section):
    images = daq.valuesOfInterval(cam_addr, section)
    checked_images = np.array([image for image in images if np.sum(image) != 0 or True])  # check for empty/NaN traces
    average_image = np.average(checked_images, axis=0)
    number_of_images = checked_images.shape[0]
    return average_image, number_of_images


def average_image_of_run(daq, cam_addr, run_number):
    total_trainID_inteval = daq.pulseIdIntervalOfRun(cam_addr, run_number)
    section_length = 100
    sections = section_ID_intervals(total_trainID_inteval, section_length)
    list_comp = np.array([average_image_and_weight_of_section(daq, cam_addr, section) for section in sections])
    image = np.average(list_comp[:, 0], axis=0, weights=list_comp[:, 1])
    return image


def print_existing_datasets(root_dir, run_number, contains=None):
    daqs = ['fl1user1', 'fl1user2', 'fl1user3', 'fl2user1', 'fl2user2', 'pbd', 'pbd2']

    def visitor_func(name, node):
        if isinstance(node, h5py.Dataset):
            if contains == None:
                print(node.name)
            elif contains in node.name:
                print(node.name)

    for daq in daqs:
        files = glob.glob(f'{root_dir}{daq}/*run{run_number}*')
        try:
            with h5py.File(files[0], 'r') as h_file:
                h_file.visititems(visitor_func)
        except IndexError:
            pass
