import numpy as np
from scipy.ndimage.interpolation import shift


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
