from camp.timepix_run import TimePixRun
from pprint import pprint

run_number = 864  # short run

timepix_run = TimePixRun(run_number)
pprint(timepix_run.__dict__)

flash_run_number = timepix_run.get_flash_run_number()
print(f'corresponding FLASH DAQ run number: {flash_run_number}')

triggers, trainIDs = timepix_run.get_trainIDs()
print(len(triggers), len(trainIDs))
