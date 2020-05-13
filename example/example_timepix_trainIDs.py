from camp.timepix_run import TimePixRun
from pprint import pprint

run_number = 863  # run with trainIDs cut off at the end

timepix_run = TimePixRun(run_number)

pprint([x for x in dir(timepix_run) if not x.startswith('_')])

flash_run_number = timepix_run.get_flash_run_number()
print(f'corresponding FLASH DAQ run number: {flash_run_number}')

triggers, trainIDs = timepix_run.get_trainIDs()
print(f'Number of triggers: {len(triggers)} | Number of TrainIDs {len(trainIDs)}')

print(f'correlation coefficient: {timepix_run.corr_coeff}')
