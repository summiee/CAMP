import camp.pydoocs_utils as cpu
import matplotlib.pyplot as plt

filename = '../data/test.h5'
train_file = cpu.TrainFile(filename)

with train_file:
    train_file.contains()

with train_file:
    macropulses = train_file.get_channel_data('macropulse')
    traces = train_file.get_channel_data('data')

for train in range(len(macropulses)):
    plt.plot(traces[train][:, 0], traces[train][:, 1], label='trainID = {}'.format(macropulses[train]))
plt.legend()
plt.show()
