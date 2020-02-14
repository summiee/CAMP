import matplotlib.pyplot as plt
import numpy as np


def return_list_of_uniques(input_list):
    output = list(set(input_list))
    return output

def create_image_with_cirlce(size = (400,400), center = (100,100)):
    xx, yy = np.mgrid[:size[0], :size[1]]
    circle = (xx - center[0]) ** 2 + (yy - center[1]) ** 2
    return np.logical_and(circle < (6400 + 600), circle > (6400 - 600))*1 # multiply by 1 to transform to ints

class trace:

    def __init__(self, values, label=None, unit=None):
        self.array = np.array(values)
        self.length = len(self.array)
        self.label = label
        self.unit = unit

    def __str__(self):
        return str(self.array)


class XYPlot:

    def __init__(self, x, y, title=None, xlabel=None, ylabel=None):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def add_label(self):
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)

    def show(self):
        self.create()
        plt.show()

    def hist_to_xy(self, array, bins):
        hist = np.histogram(array, bins=bins)
        y, x = [hist[0], 0.5 * (hist[1][1:] + hist[1][:-1])]
        return x, y


class LinePlot(XYPlot):
    linewidth = 1

    def __init__(self, x, y, title=None, xlabel=None, ylabel=None):
        super().__init__(x, y, title, xlabel, ylabel)

    def create(self):
        fig = plt.plot(self.x, self.y, linewidth=self.linewidth)
        self.add_label()


class ScatterPlot(XYPlot):
    markersize = 10

    def __init__(self, x, y, title=None, xlabel=None, ylabel=None):
        super().__init__(x, y, title, xlabel, ylabel)

    def create(self):
        plt.scatter(self.x, self.y, s=self.markersize)
        self.add_label()


class Hist2D(XYPlot):

    def __init__(self, x, y, bins, title=None, xlabel=None, ylabel=None):
        super().__init__(x, y, title, xlabel, ylabel)
        self.bins = bins

    def create(self):
        plt.hist2d(self.x, self.y, bins=self.bins)
        self.add_label()


class MultiplePlots:

    def __init__(self, *argv):
        for i in range(len(argv)):
            plt.figure(i)
            argv[i].create()
        plt.show()
