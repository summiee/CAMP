from camp.timepix_run import TimePixRun

run_number = 864  # short run

timepix_run = TimePixRun(run_number)

triggers, trainIDs = timepix_run.get_trainIDs()
print(len(triggers), len(trainIDs))
