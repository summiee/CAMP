from camp.timepix_run import TimePixRun
from pprint import pprint

run_number = 863  # run with trainIDs cut off at the end

timepix_run = TimePixRun(run_number)
pprint(dir(timepix_run))

print('###')

flash_run_number = timepix_run.get_flash_run_number()
print(f'corresponding FLASH DAQ run number: {flash_run_number}')

triggers, trainIDs = timepix_run.get_trainIDs()
print(len(triggers), len(trainIDs))
