import numpy as np
from scipy.optimize import curve_fit

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Image():
    """ Image object with profiles """

    def __init__(self, array):
        self.image = array
        self.shape = array.shape
        self.x_profile = np.sum(array, axis=0)
        self.y_profile = np.sum(array, axis=1)
        self.max_value = np.max(array)
        self.number_of_max_pixel = np.count_nonzero(array == self.max_value)
        self.__fit_profiles()
        self.x_mean = np.argmax(self.x_profile_fitted)
        self.y_mean = np.argmax(self.y_profile_fitted)

    def show(self):
        fig = px.imshow(self.image)
        fig.update_layout(coloraxis={'colorscale': 'viridis'})
        fig.show()

    def plot_profiles(self):

        fig = make_subplots(rows=2, cols=1, subplot_titles=("X profile", "Y profile"))

        fig.append_trace(go.Scatter(x=np.linspace(0, len(self.x_profile) - 1, len(self.x_profile)),
                                    y=self.x_profile_fitted,
                                    line=dict(color='rgb(158,202,225)')),
                         row=1, col=1)

        fig.append_trace(go.Bar(y=self.x_profile,
                                marker_color='lightsalmon'),
                         row=1, col=1)

        fig.append_trace(go.Scatter(x=np.linspace(0, len(self.y_profile) - 1, len(self.y_profile)),
                                    y=self.y_profile_fitted,
                                    line=dict(color='rgb(158,202,225)')),
                         row=2, col=1)

        fig.append_trace(go.Bar(y=self.y_profile,
                                marker_color='lightsalmon'),
                         row=2, col=1)

        fig.update_layout(title_text="Profiles", showlegend=False)
        fig.update_xaxes(title_text=f"x_mean: {self.x_mean}", row=1, col=1)
        fig.update_xaxes(title_text=f"y_mean: {self.y_mean}", row=2, col=1)
        fig.show()

    def __gauss(self, x, a, mean, sigma, offset):
        return a * np.exp(-(x - mean) ** 2 / (2 * sigma ** 2)) + offset

    def __fit_params_gauss(self, y):
        x = np.linspace(0, len(y) - 1, len(y))
        n = np.sum(y)
        mean = np.sum(y * x) / n
        sigma = np.sqrt(np.sum(y * (x - mean) ** 2) / n)
        popt, pcov = curve_fit(self.__gauss, x, y, p0=[1, mean, sigma, 0.0])
        return popt

    def __fit_profiles(self):
        self.x_profile_fitted = self.__gauss(np.linspace(0, len(self.x_profile) - 1, len(self.x_profile)),
                                             *self.__fit_params_gauss(self.x_profile))
        self.y_profile_fitted = self.__gauss(np.linspace(0, len(self.y_profile) - 1, len(self.y_profile)),
                                             *self.__fit_params_gauss(self.y_profile))

    def describe(self):
        attributes = ['shape', 'max_value', 'number_of_max_pixel', 'x_mean', 'y_mean']
        for attribute in attributes:
            if attribute in self.__dict__.keys():
                print(f'{attribute} : {self.__dict__[attribute]}')
