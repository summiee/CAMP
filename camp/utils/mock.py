import numpy as np


def create_image_with_cirlce(size=(400, 400), center=(100, 100)):
    xx, yy = np.mgrid[:size[0], :size[1]]
    circle = (xx - center[0]) ** 2 + (yy - center[1]) ** 2
    return np.logical_and(circle < (6400 + 600), circle > (6400 - 600)) * 1  # multiply by 1 to transform to ints


def create_fake_image(size=256, fwhm=100, center=None, noise=None):
    """ Make a square gaussian kernel.

    size is the length of a side of the square
    fwhm is full-width-half-maximum, which can be thought of as an effective radius.
    center can be (x0,y0)
    noise with mu=0
    """

    x = np.arange(0, size, 1, float)
    y = x[:, np.newaxis]

    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]

    gauss_image = np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / fwhm ** 2)

    if noise is None:
        return gauss_image
    else:
        mu, sigma = 0, noise
        gauss_noise = np.random.normal(mu, sigma, (size, size))
        return gauss_image + gauss_noise


def create_fake_trace(length, A=1, shift=0, noise=None):
    """ Make a shifted sinus with noise """

    if noise is None:
        return A * np.sin(np.arange(0, length, 1) / 10 + shift)
    else:
        mu, sigma = 0, noise
        return A * np.sin(np.arange(0, length, 1) / 10 + shift) + np.random.normal(mu, sigma, length)



