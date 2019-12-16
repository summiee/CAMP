# -*- coding: utf-8 -*-

import numpy as np  
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import h5py

def unique(list_to_check):  
    unique_list = [] 
    for x in list_to_check: 
        if x not in unique_list: 
            unique_list.append(x) 
    return unique_list

def load_radial_data(file_name, load_from_path, fragment_list):
    runs = []
    delay_stage_pos = []
    number_of_trains = []

    list_of_lists = [[] for i in range(len(fragment_list))]            

    with h5py.File(load_from_path+file_name, 'r') as f:

        for key in f.keys():
            runs.append(key)

        for i in range(len(runs)):
            delay_stage_pos.append(np.array(f[str(runs[i])+'/delay_stage']))
            number_of_trains.append(np.array(f[str(runs[i])+'/number_of_trains']))

            for j in range(len(fragment_list)):
                list_of_lists[j].append(np.array(f[str(runs[i])+'/'+str(fragment_list[j])+'/radial_average']))

    number_of_trains = np.array(number_of_trains)
    delay_stage_pos = np.array(delay_stage_pos)

    sort_ind = np.argsort(delay_stage_pos)
    number_of_trains = number_of_trains[sort_ind]
    delay_stage_pos = delay_stage_pos[sort_ind]

    for i in range(len(fragment_list)):
        list_of_lists[i] = np.array(list_of_lists[i])
        list_of_lists[i] = list_of_lists[i][sort_ind]
        for j in range(len(runs)):
            list_of_lists[i][j] = list_of_lists[i][j]/number_of_trains[j]

    uni_delay = np.array(unique(delay_stage_pos))
    uni_list_of_lists = [[] for i in range(len(fragment_list))]

    for i in range(len(fragment_list)):
        for k in range(len(uni_delay)):
            tt = []
            number_to_norm = 0
            for j in range(len(delay_stage_pos)):
                if uni_delay[k] == delay_stage_pos[j]:
                    number_to_norm = number_to_norm +1
                    tt.append(list_of_lists[i][j])
            uni_list_of_lists[i].append((np.sum(np.array(tt),axis = 0)/number_to_norm))
        uni_list_of_lists[i] = np.array(uni_list_of_lists[i])

    print('number of runs:',len(delay_stage_pos))
    print('number of unqique delays:',len(uni_delay))
#     print('shape of radial averages with unique dealy:',np.array(uni_list_of_lists).shape)

    return fragment_list, uni_delay, uni_list_of_lists
        
def simple_plots(fragment_list, uni_delay, uni_list_of_lists):
    for k in range(len(fragment_list)):
        colors = cm.rainbow(np.linspace(0, 1, len(uni_list_of_lists[k])))
        fig = plt.figure(figsize = (10,10), num = k)
        for i in range(len(uni_list_of_lists[k])):
            plt.plot(uni_list_of_lists[k][i],label=uni_delay[i], color = colors[i])
        plt.xlabel('r')
        plt.ylabel('counts')
        plt.legend()
        plt.title(str(fragment_list[k]), fontsize = 20)

def heatmap(fragment_list, uni_delay, uni_list_of_lists):
    for k in range(len(fragment_list)):
        fig = plt.figure(figsize = (10,10),num = k+len(fragment_list))
        image = np.column_stack(uni_list_of_lists[k])
        plt.imshow(image, aspect="auto", origin="lower")
        plt.xticks(np.arange(len(uni_delay)), uni_delay)
        plt.title(str(fragment_list[k]), fontsize = 20)

def x_projection_heatmap(fragment_list, uni_delay, uni_list_of_lists):
    for k in range(len(fragment_list)):
        intensities_per_delay = np.sum(uni_list_of_lists[k],axis =1)
        fig = plt.figure(figsize = (10,10),num = k+len(fragment_list)*2)
        plt.plot(uni_delay, intensities_per_delay,'o')
        plt.xlabel('delay')
        plt.ylabel('integral of radial average')
        plt.title(str(fragment_list[k]), fontsize = 20)