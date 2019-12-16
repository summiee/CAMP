# -*- coding: utf-8 -*-

import numpy as np  
import matplotlib.pyplot as plt
import h5py
import os.path
import src.pyabel_polar
import scipy
import yaml

file_system = 'core'
config_file = 'src/config.yaml'
pp_delay_file = 'src/run_pp-delay.txt'

def generate_hdf_file_name(run_number):
    global file_system, config_file
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    hdf_file_path = cfg['path'][file_system]
    try:
        file_start = "run_"+str(run_number).zfill(4)
        not_file_end = 'rawOnly.hdf5'
        hdf_file = [i for i in os.listdir(hdf_file_path) if os.path.isfile(os.path.join(hdf_file_path,i)) and i.startswith(file_start) and not i.endswith(not_file_end)][0]
        hdf_file_complete_path = hdf_file_path+hdf_file
        assert os.path.isfile(hdf_file_complete_path), 'File does not exist!'
        return hdf_file_complete_path
    except IndexError:
        print("Run",run_number,"do not exist!")

def data_from_hdf(hdf_file_complete_path, event_type = 'raw'):
    '''Read data from TimePix HDF files
    Choose raw or centroided data, default is centroided data'''
    with h5py.File(hdf_file_complete_path, 'r') as h_file:
        tof = h_file[str(event_type)+'/tof'][:]
        x_pos = h_file[str(event_type)+'/x'][:]
        y_pos = h_file[str(event_type)+'/y'][:]
    print('Number of raw events in the file: {0:.3E}'.format(len(tof)))
    print('Number of FEL pulses in the file: {0:.3E}'.format(number_of_trains_from_hdf(hdf_file_complete_path)))
    return tof, x_pos, y_pos

def data_sliced_by_tof(hdf_file_complete_path, tof_start = 0 , tof_end = 0.1, event_type = 'raw'):
    '''Slice data with respect to time-of-flight dimension'''
    tof, x_pos, y_pos = data_from_hdf(hdf_file_complete_path, event_type)
    sliced_x_pos = x_pos[np.logical_and(tof > tof_start, tof < tof_end)]
    sliced_y_pos = y_pos[np.logical_and(tof > tof_start, tof < tof_end)]
    sliced_tof = tof[np.logical_and(tof > tof_start, tof < tof_end)]
    return sliced_tof, sliced_x_pos, sliced_y_pos

def data_sliced_by_fragment(hdf_file_complete_path, fragment, event_type = 'raw'):
    '''Slice data with respect to time-of-flight dimension'''
    tof_start, tof_end = get_tof_limits_for_fragment(fragment)
    tof, x_pos, y_pos = data_from_hdf(hdf_file_complete_path, event_type)
    sliced_x_pos = x_pos[np.logical_and(tof > tof_start, tof < tof_end)]
    sliced_y_pos = y_pos[np.logical_and(tof > tof_start, tof < tof_end)]
    sliced_tof = tof[np.logical_and(tof > tof_start, tof < tof_end)]
    return sliced_tof, sliced_x_pos, sliced_y_pos

def reduce_raw_data(tof, x_pos, y_pos, number_of_events):
    '''Reduce data for visualization'''
    return tof[:number_of_events], x_pos[:number_of_events],y_pos[:number_of_events]

def number_of_trains_from_hdf(hdf_file_complete_path):
    '''Retrun number of recorded FEL trains in HDF file'''
    with h5py.File(hdf_file_complete_path, 'r') as h_file:
        trains = len(h_file['tpx3Times/triggerNr'][:])
    return trains

def tof_conversion(tof, time_unit):
    '''Convert time axis'''
    if time_unit == None:
        return tof, 's'
    if time_unit == 'milli':
        return tof*10**3, 'ms'
    if time_unit == 'micro':
        return tof*10**6, 'us'

def plot_tof(tof, tof_start = None, tof_end = None, hist_bins = 100, time_unit = None):     
    '''Plot time-of-flight spectrum via numpy histogram'''
    if tof_start == None:
        tof_start = np.min(tof)
    if tof_end == None:
        tof_end = np.max(tof)
        
    tof_start, time_tof_unit = tof_conversion(tof_start, time_unit)
    tof_end, time_tof_unit = tof_conversion(tof_end, time_unit)
    tof, time_tof_unit = tof_conversion(tof, time_unit)
    
    fig = plt.subplots(num = 1)
    plt.clf()
    hist_y, hist_x = np.histogram(tof, bins = hist_bins, range = (tof_start, tof_end))
    hist_y = np.append(hist_y,0)
    plt.plot(hist_x, hist_y)
    plt.title('histogram: time-of-flight')
    plt.xlabel('ToF [{}]'.format(time_tof_unit))
    plt.ylabel('number of events')
    plt.show()
    return hist_x, hist_y
        
def plot_1d_histograms(tof, x_pos, y_pos, time_unit = None):      
    '''1D plots - detector position vs time-of-flight for each dimension'''
    tof, time_tof_unit = tof_conversion(tof, time_unit)
    fig = plt.figure(num = 2)
    plt.clf()
    plt.plot(tof, x_pos,'.')
    plt.title("ToF vs x_pos")
    plt.xlabel('ToF [{}]'.format(time_tof_unit))
    plt.ylabel('x_pos [px]')
    
    fig = plt.figure(num=3)
    plt.clf()
    plt.plot(tof, y_pos,'.')
    plt.title("ToF vs y_pos")
    plt.xlabel('ToF [{}]'.format(time_tof_unit))
    plt.ylabel('y_pos [px]')
    plt.show()

def plot_2d_histograms(tof, x_pos, y_pos ,bin_tof = 6000, bin_space = 256, time_unit = None, colormin = 0, colormax = 1000):
    '''2D plot (heatmap) - detector position vs time-of-flight for each dimension'''
    
    tof, time_tof_unit = tof_conversion(tof, time_unit)

    fig = plt.figure(num = 4)
    plt.clf()
    plt.hist2d(tof, x_pos, bins = (bin_tof, np.linspace(0, bin_space, bin_space+1)), cmax=colormax)
    plt.title('2d histogram: time-of-flight / x_pos')
    plt.xlabel('ToF [{}]'.format(time_tof_unit))
    plt.ylabel('x_pos')
    plt.show()
    plt.colorbar()
    
    fig = plt.figure(num = 5)
    plt.clf()
    plt.hist2d(tof, y_pos,bins= (bin_tof, np.linspace(0, bin_space, bin_space+1)), cmax=colormax)
    plt.title('2d histogram: time-of-flight / y_pos')
    plt.xlabel('ToF [{}]'.format(time_tof_unit))
    plt.ylabel('y_pos')
    plt.show()
    plt.colorbar()
    
def vmi_image(x_pos, y_pos, show_image = True):
    '''Display VMI image - cmax empirically found to surpress hot pixel '''
    fig = plt.figure(num = 6)
    plt.clf()
    counts, xbins, ybins, image = plt.hist2d(x_pos, y_pos, bins=np.linspace(0, 256, 257)) #, cmax= 1000)
    plt.xlabel('x_pos [px]')
    plt.ylabel('y_pos [px]')
    if show_image == False:
        plt.close()
    return counts
    
def display_tof_and_vmi_of_tof_interval(hdf_file_complete_path, fragment, hist_bins = 100, time_unit = None, event_type = 'raw'):
    '''Display VMI Image and time-of-flight spetrum'''
    tof_start, tof_end  = get_tof_limits_for_fragment(fragment)
    tof, x_pos, y_pos = data_sliced_by_tof(hdf_file_complete_path, tof_start, tof_end, event_type)
    plot_tof(tof, hist_bins = hist_bins, time_unit = time_unit)
    vmi_image(x_pos,y_pos)

def transform_vmi_to_polar(x_pos, y_pos, fragment, radius = None, show_images = True):
    
    x_center , y_center = get_vmi_center_for_fragment(fragment)
    counts = vmi_image(x_pos, y_pos, show_image = False)
    image_cart = counts.transpose()
    
    image_polar, r_grid, theta_grid = src.pyabel_polar.reproject_image_into_polar(image_cart, origin=(x_center,y_center))
    radial_ave = np.sum(image_polar, axis=1)
    
    if show_images == True: 
        fig = plt.figure(num = 6)
        plt.clf()
        plt.imshow(image_cart)
        plt.scatter(x_center, y_center, color='r')
        if radius != None:
            plt.gcf().gca().add_artist(plt.Circle((x_center, y_center), radius, color='r', fill=False))
        plt.xlabel('x_posr [px]')
        plt.ylabel('y_posr [px]')
        plt.title('VMI image')

        fig = plt.figure(num = 7)
        plt.clf()
        plt.imshow(image_polar)
        plt.title('Image - polar coordinates')

        fig = plt.figure(num = 8)
        plt.clf()
        plt.plot(radial_ave,'r-')
        plt.title('Radial average')
        plt.xlabel('r [px]')
        plt.ylabel('counts')
    
    return radial_ave
    
def get_vmi_center_for_fragment(fragment):
    global file_system, config_file
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    center_x = cfg['fragments'][fragment]['center_x']
    center_y = cfg['fragments'][fragment]['center_y']
    return center_x, center_y

def get_tof_limits_for_fragment(fragment):
    global file_system, config_file
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    tof_start = cfg['fragments'][fragment]['tof_start']
    tof_end = cfg['fragments'][fragment]['tof_end']
    return tof_start, tof_end

def get_train_numbers_from_files(run_interval):
    number_of_trains = []
    runs = []
    for i in range(run_interval[0], run_interval[1]+1):
        runs.append(i)
        hdf_file = generate_hdf_file_name(i)
        if hdf_file != None:
            number_of_trains.append(number_of_trains_from_hdf(hdf_file))
        elif hdf_file == None:
            number_of_trains.append(0)
    return runs, number_of_trains

def unique(list_to_check):  
    unique_list = [] 
    for x in list_to_check: 
        if x not in unique_list: 
            unique_list.append(x) 
    return unique_list

def get_trains_vs_unique_delay(delay_pos, trains):
    unique_delay_pos = unique(delay_pos)
    unique_trains = []
    for i in range(len(unique_delay_pos)):
        tt = []
        for j in range(len(delay_pos)):
            if unique_delay_pos[i] == delay_pos[j]:
                tt.append(trains[j])
        unique_trains.append(np.sum(np.array(tt)))
    sort_ind = np.argsort(np.array(unique_delay_pos))
    unique_delay_pos = np.array(unique_delay_pos)[sort_ind]
    unique_trains = np.array(unique_trains)[sort_ind]
    return unique_delay_pos, unique_trains

def plot_number_of_trains_vs_run(run_interval): 
    runs, trains = get_train_numbers_from_files(run_interval)              
    fig = plt.figure(figsize = (10,10))
    plt.plot(runs,trains,'o')
    plt.ylabel('FEL pulses')
    plt.xlabel('Run Number')
    plt.title('FEL trains in Runs')
    plt.show()
        
def list_number_of_trains_vs_run(run_interval): 
    runs, trains = get_train_numbers_from_files(run_interval)
    for i in range(len(runs)):
        print('RunNumber:',runs[i],'| number of trains:',trains[i])

def plot_number_of_trains_vs_delay(run_interval):
    runs, trains = get_train_numbers_from_files(run_interval)
    runs_pp, delay_pos = get_delay_stage_pos_from_txt_file(run_interval)
    assert runs == runs_pp, 'Runs are not identical!'
    unique_delay_pos, unique_trains = get_trains_vs_unique_delay(delay_pos, trains)
    fig = plt.figure(figsize = (10,10))
    plt.plot(unique_delay_pos,unique_trains,'o')
    plt.ylabel('FEL pulses')
    plt.xlabel('Delay position')
    plt.title('FEL trains in delay position')
    plt.show()
        
def list_number_of_trains_vs_delay(run_interval):
    runs, trains = get_train_numbers_from_files(run_interval)
    runs_pp, delay_pos = get_delay_stage_pos_from_txt_file(run_interval)
    assert runs == runs_pp, 'Runs are not identical!'
    unique_delay_pos, unique_trains = get_trains_vs_unique_delay(delay_pos, trains)
    for i in range(len(unique_delay_pos)):
        print('Delay Position:', unique_delay_pos[i],'| number of trains:',unique_trains[i])           

def get_delay_stage_pos_from_txt_file(run_interval):
    global pp_delay_file
    runs = []
    delay_pos = []
    filepath = pp_delay_file
    with open(filepath) as fp:
        for cnt, line in enumerate(fp):
            tt = [x.strip() for x in line.split(',')]
            runs.append(int(tt[0]))
            delay_pos.append(float(tt[1]))
    delay_pos = delay_pos[runs.index(run_interval[0]):runs.index(run_interval[1])+1]
    runs = runs[runs.index(run_interval[0]):runs.index(run_interval[1])+1]
    return runs, delay_pos
