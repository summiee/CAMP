import numpy as np
from camp.utils.mock import create_fake_trace
from camp.utils.heatmap import Heatmap

scale, offset, quantity = 10, -5, 1000
delays = scale * np.random.random(quantity) + offset

keys = ['delay','trace']
data = {key: [] for key in keys}

length_of_trace = 300
for delay in delays:
    trace = create_fake_trace(length_of_trace, shift=delay, noise=0.3)
    data['delay'].append(delay)
    data['trace'].append(trace)

bins = [-5, 5, 1]

heatmap = Heatmap(data['trace'], data['delay'], bins)
heatmap.show()
heatmap.frequency()