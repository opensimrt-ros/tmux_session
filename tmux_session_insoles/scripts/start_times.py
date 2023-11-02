#!/usr/bin/env python3
# vim:fenc=utf-8

#
# @author      : frekle (frekle@bml01.mech.kth.se)
# @file        : start_times
# @created     : Tuesday Oct 17, 2023 16:09:35 CEST
#

# generate the start times for the insoles since we didn't save the arrival timestamps 
# NOTE: the arrival will be with a fixed frequency of 100hz even though it may not have been recorded like that.
# this type of data would not play in real-time, so this is a hack.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import os

def generate_start_times_everyone(ik_files, insole_files):

    ik_df = []
    for ik_file in ik_files :
        ik_df.append(pd.read_csv(ik_file, skiprows=4, sep=r'\t', engine='python'))

    ik_start_times = []    
    for ik_dfi in ik_df:
        ik_start_times.append(ik_dfi.time.values[0])
    insole_df = []
    for insole_file in insole_files :
        insole_df.append(pd.read_csv(insole_file, sep=r'\s+'))

    insole_start_times_left = []
    insole_start_times_right = []
    for insole_dfi in insole_df:
        insole_start_times_left.append(insole_dfi[insole_dfi["side"]==0].Frame.values[0])
        insole_start_times_right.append(insole_dfi[insole_dfi["side"]==1].Frame.values[0])

    start_times_if_left = list((insole_start_times_left - insole_start_times_left[0])/1000+ik_start_times[0])
    #print(start_times_if_left)

    start_times_if_right = list((insole_start_times_right -insole_start_times_right[0])/1000+ik_start_times[0])
    #print(start_times_if_right)

    side_start_picker = []
    for iii in insole_df:
        side_start_picker.append(iii.iloc[0].side)
        #if (iii.iloc[0].side):
        #    print("right")
        #else:
        #    print("left")
    #print(side_start_picker)

    #now if it is one side or the other I will need to choose the different starting times:
    start_times_picked = []   
    for st_time_l, st_time_r, ppp in zip(start_times_if_left, start_times_if_right, side_start_picker):
        if ppp:
            start_times_picked.append(st_time_r)
        else:
            start_times_picked.append(st_time_l)

    ##choose a better name, this is the insole start times        
    #print(start_times_picked)

    #but we want this as a tuple of secs and nsecs both as integers
    t_ik = []
    for ik_i in ik_start_times:
        t_ik.append((int(ik_i), int(1e9*(ik_i-int(ik_i)))))

    clock_t = []
    #print(ik_start_times)
    #print(start_times_picked)
    for tt, it in zip(ik_start_times, start_times_picked):
        earliest_start_time = int(np.floor(np.min([tt,it]))) ## we have to start before the earliest start time
        print("Time difference between ik start times and insole start times: %f"%(tt-it))
        clock_t.append((earliest_start_time-1,0))
    
    print("insole_start = %s"%(",\n\t".join(str(start_times_picked).split(","))))
    print("ik_start = %s"%("),\n\t".join(str(t_ik).split("),"))))
    print("clock_start = %s"%("),\n\t".join(str(clock_t).split("),"))))
    return start_times_picked, t_ik, clock_t

def gen_action_nums(directory, action):
    ik_file_glob = "%s/*%s*ik_lower.sto"%(directory, action)
    #print(ik_file_glob)
    ik_files_action = glob(ik_file_glob) #path join? do i want to recurse subdirs
    ik_files_action.sort()
    #print(ik_files_action)
    insole_files_action = glob("%s/*%s*corrected*.txt"%(directory, action))
    insole_files_action.sort()
    #print(insole_files_action)
    
    print("common_path = '%s'"%directory)
    common_path = directory
    fff = [os.path.basename(ikf) for ikf in ik_files_action]
    insole_files_minus_dir = [os.path.basename(inf) for inf in insole_files_action]
    #for ikf in ik_files_action:
    #    ik_files_minus_dir.append(ikf.split(directory)[])

    print("fff = %s"%(",\n\t".join(str(fff).split(","))))
    ## creating the tuples is a bit more involved and i cant do a one liner
    parameter_tuples = [f"('%s/{tt}'%common_path,'%s/%s'%(common_path,fff[{ii}]),'02')" for ii,tt in enumerate(insole_files_minus_dir)]
    #print(parameter_tuples)
    parameter_str = "["
    for a_param in parameter_tuples:
        parameter_str += a_param+",\n"
    parameter_str += "]"
    print("parameter_tuples = %s"%(parameter_str))
    insole_start, ik_start, clock_start = generate_start_times_everyone(ik_files_action, insole_files_action)
    print("action='%s'"%action)
    return common_path, fff,parameter_str, insole_start,ik_start,clock_start

def main():
    pass

if __name__ == '__main__':
	main()



