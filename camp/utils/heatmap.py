import numpy as np
from camp.utils.utils import print_table
import plotly.express as px

class Heatmap():
    """ Heatmap object which can be binned

    bins = [first_bin, last_bin, bin_width]
    """

    def __init__(self, traces, delays, binning):
        self.traces = traces
        self.delays = delays
        self.__create_image(binning)

    def __create_image(self, binning):
        self.bins = np.linspace(binning[0], binning[1], (binning[1] - binning[0]) / binning[2] + 1)
        self.image = np.zeros((len(self.traces[0]), len(self.bins)), dtype=float)
        self.weights = np.zeros(len(self.bins), dtype=int)

        for i in range(len(self.bins)):
            trace_temp = []
            weight_temp = 0
            for j in range(len(self.delays)):
                if self.delays[j] >= self.bins[i] - binning[2] / 2 and self.delays[j] < self.bins[i] + binning[2] / 2:
                    trace_temp.append(self.traces[j])
                    weight_temp += 1
            self.image[:, i] = np.average(trace_temp, axis=0)
            self.weights[i] = weight_temp

    def show(self, colorbar=False, colorscale='viridis', x_ticks_on=True):
        fig = px.imshow(self.image)
        fig.update_layout(xaxis=dict(scaleanchor="y",
                                     scaleratio=self.image.shape[0] / self.image.shape[1],
                                     ticks="outside",
                                     tickmode='array',
                                     tickvals=(self.bins - self.bins[0]) * 1 / (self.bins[1] - self.bins[0]),
                                     ticktext=self.bins,
                                     visible=x_ticks_on),
                          coloraxis={'colorscale': colorscale,
                                     'showscale': colorbar})
        fig.show()

    def frequency(self):
        print_table([self.bins, self.weights])