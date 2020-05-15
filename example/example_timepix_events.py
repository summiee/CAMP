from camp.timepix_run import TimePixRun, Filter

run_number = 863
timepix_run = TimePixRun(run_number)

event_type = 'raw'
parameters = ['x', 'y', 'tof', 'tot']

timepix_dict = timepix_run.get_events(event_type, parameters)

print(timepix_dict.keys())
print(len(timepix_dict['x']))

filter_1 = Filter('tof', 0, 1E-6)
filter_2 = Filter('x', 100, 200)

timepix_dict = timepix_run.get_events(event_type, parameters, filter_1, filter_2)

print(timepix_dict.keys())
print(len(timepix_dict['x']))

fragment = 'fragments,test_ion'

timepix_dict = timepix_run.get_events(event_type, parameters, fragment=fragment)

print(timepix_dict.keys())
print(len(timepix_dict['x']))


