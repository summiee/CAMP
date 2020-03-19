from camp.pydoocs_utils import TrainAbo

doocs_addr = 'FLASH.FEL/ADC.SIS.BL1/EXP1.CH00/CH00.TD'  # MHz ADC
train_abo = TrainAbo(doocs_addr)

# print keys
print(train_abo.channel_keys())

# yield pydoocs_dict as generator
for channel in train_abo.trains(3):
    print(channel['macropulse'])

# save train_abo to HDF5 file
key_list = ['data', 'timestamp', 'macropulse', 'type', 'miscellaneous']
filename = '../data/test.h5'

train_abo.to_hdf(filename, key_list, 3)
