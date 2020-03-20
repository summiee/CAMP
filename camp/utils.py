import numpy as np
from scipy.ndimage.interpolation import shift


def return_list_of_uniques(input_list):
    output = list(set(input_list))
    return output


def create_image_with_cirlce(size=(400, 400), center=(100, 100)):
    xx, yy = np.mgrid[:size[0], :size[1]]
    circle = (xx - center[0]) ** 2 + (yy - center[1]) ** 2
    return np.logical_and(circle < (6400 + 600), circle > (6400 - 600)) * 1  # multiply by 1 to transform to ints


def hist_to_xy(array, bins):
    hist = np.histogram(array, bins=bins)
    y, x = [hist[0], 0.5 * (hist[1][1:] + hist[1][:-1])]
    return x, y


def find_nearest(array, values):
    indices = np.abs(np.subtract.outer(array, values)).argmin(0)
    return indices


def missing_elements(list):
    start, end = list[0], list[-1]
    return sorted(set(range(start, end + 1)).difference(list))


def cfd(signal, fraction, delay=1, threshold=0):
    """Constant Fraction Discriminator

    :param np.array signal: the input from the digitizer
    :param float fraction: the fraction, from 0 to 1
    :param float delay: the delay of the CFD
    :param float threshold: the threshold
    :return np.array edge_indices: the start and stop indices for each peak
    """

    # Scaled and delayed signal
    scaled = signal * fraction
    delayed = shift(scaled, -delay, mode="nearest")
    cfd_signal = signal - delayed

    # Edge detection
    edges_bool = cfd_signal > threshold
    edges_bool_2 = edges_bool[1:] != edges_bool[:-1]
    edge_indices = np.squeeze(np.where(edges_bool_2 == True))

    return edge_indices
