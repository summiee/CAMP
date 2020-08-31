import numpy as np


def hist_to_xy(array, bins):
    hist = np.histogram(array, bins=bins)
    y, x = [hist[0], 0.5 * (hist[1][1:] + hist[1][:-1])]
    return x, y


def find_nearest(array, values):
    indices = np.abs(np.subtract.outer(array, values)).argmin(0)
    return indices


def check_for_completeness(list):
    start, end = int(list[0]), int(list[-1])
    return sorted(set(range(start, end + 1)).difference(list))


def print_table(table):
    longest_cols = [(max([len(str(row[i])) for row in table]) + 3) for i in range(len(table[0]))]
    row_format = "".join(["{:>" + str(longest_col) + "}" for longest_col in longest_cols])
    for row in table:
        print(row_format.format(*row))
