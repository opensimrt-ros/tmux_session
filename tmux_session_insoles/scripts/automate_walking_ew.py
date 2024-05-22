#!/bin/env python3

USE_TIMEOUT=True
#USE_TIMEOUT=False

trials_to_run = [8]

#clock_slowdown_rate= 1
clock_slowdown_rate=1

timeout_time = 30
#timeout_time = 80

with_rotation = False


weight=62.3
height=1.70 #??
default_urdf_model_height=1.75 #???
##we have to scale the urdf model...

ik_delay=3.0

action="walking"

id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT3.bash'

angle=-60.87

#model_file="/srv/host_data/02_ruoli/gait2392_simbody_RW.osim"
model_file="/srv/host_data/04_ew/S4_scaled.osim"
moment_arm_lib="/catkin_ws/devel/lib/Gait2392MomentArm_RW"

common_path ='/srv/host_data/04_ew/ViconData/Ruoli/Motion_Insole/RealTimeIkIDS4' 
#ik_list = glob.glob("%s/*walking*_ik_lower.sto"%common_path)
#ik_list.sort()
#insole_list = glob.glob("%s/walking*_header_corrected.txt"%common_path)
#insole_list.sort()
#parameter_tuples = []

#for insole_file. ik_file in zip(insole_list, ik_list):
#    parameter_tuples.append((insole_file. ik_file))
fff = [
 "2023-03-10-10-14-59walking011_imus_lower.sto",
 "2023-03-10-10-15-39walking022_imus_lower.sto",
 "2023-03-10-10-16-43walking033_imus_lower.sto",
 "2023-03-10-10-17-03walking044_imus_lower.sto",
 "2023-03-10-10-17-24walking055_imus_lower.sto",
 "2023-03-10-10-17-46walking066_imus_lower.sto",
 "2023-03-10-10-18-10walking077_imus_lower.sto",
 "2023-03-10-10-18-37walking088_imus_lower.sto",
 "2023-03-10-10-19-01walking099_imus_lower.sto",
]

# Define a list of parameter tuples
# INSOLE FILE, IK FILE

parameter_tuples = [
    ('%s/walking01_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[0]),"04"),
    ('%s/walking02_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[1]),"04"),
    ('%s/walking03_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[2]),"04"),
    ('%s/walking04_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[3]),"04"),
    ('%s/walking05_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[4]),"04"),
    ('%s/walking06_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[5]),"04"),
    ('%s/walking07_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[6]),"04"),
    ('%s/walking08_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[7]),"04"),
    ('%s/walking09_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[8]),"04"),
    #('value1b', 'value2b'),
]

## the ik will always start at like epoch+3

# insole_start  is the time difference between them as sec, .secs (it's going to be appended)

#it's like each line is a trial
#
# then the first element of the tuple is the common insole delay and the second and third are
#insole left , insole right
#

insole_start_original = [(0.4 , 0.0  ,0.0),
                (0.1 , 0.4  ,0.0),
                (0.3 , 0.15 ,0.0),
                (0.2 , 0.65  ,0.0),
                (0.4 , 0.05  ,0.0),
                (0.0 , 0.0  ,0.7),
                (0.0  ,0.02 ,0.0),
                (0.0  ,0.0  ,0.0),
                (0.6  ,0.25 ,0.0)]

insole_start_lags_from_point_x = [
 [1.3884530000000002, 0.007698, 0.0],
 [1.096151, 0.4, 0.05389],
 [1.311547, 0.150001, 0.0],
 [1.173054, 0.803977, 0.0],
 [1.4038490000000001, 0.05, 0.0],
 [0.91916, 0.0, 0.761593],
 [0.973055, 0.058493, 0.0],
 [1.0, 0.0, 0.0],
 [1.611548, 0.257699, 0.0]]

##this is from trying with point_x

insole_start = [
 [0.6147470000000002, 0.007698, 0.900727],
 [0.26859100000000014, 0.4, 0.177031],
 [0.514776, 0.219248, 0.0],
 [0.5763900000000001, 0.803977, 0.646706],
 [0.6147460000000001, 0.119262, 0.0],
 [0.08385999999999993, 0.846849, 0.761593],
 [0.12237399999999998, 0.19703199999999998, 0.0],
 [1.0, 0.0, 0.0],
 [0.853244, 0.319264, 0.0]]

## this is a negative number in seconds
insole_starts_sooner = 1



#####################################################################
##########                                                   ########
##########                  CODE PART:                       ########
##########                                                   ########
#####################################################################

import os, sys
import subprocess
import time
import timeout_decorator
import glob
import time
import shutil
import rospkg

if with_rotation:
    grf_no_rotation = "false"
    rot_string = "with rotation"
else:
    grf_no_rotation = "true" ## we used it the other way around...
    rot_string = "WITHOUT rotation"

##TODO: maybe I want to move this to refdata
rospack = rospkg.RosPack()
tsi_pkg_path = rospack.get_path("tmux_session_insoles")
sample_notebook=os.path.join(tsi_pkg_path, "scripts", "standard_analysis.ipynb")

ref_data_dir = "/srv/host_data/refdata"

sys.path.append(ref_data_dir)

import refdata.merge_grfs

def bling(s=None):
  if not s:
    s= '/\\' * 40
  s = s.ljust(80)
  for col in range(0, 77):
    r = 255 - col * 255 // 76
    g = col * 510 // 76
    b = col * 255 // 76
    if g > 255:
      g = 510 - g
    print(f'\x1b[48;2;{r};{g};{b}m\x1b[38;2;{255-r};{255-g};{255-b}m{s[col]}\x1b[0m', end='')
  print()


def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
    time.sleep(3)
# Path to your bash script

def strn(f):
    n = int(f)
    r = f - n
    return str(n),str(abs(r)).replace("0.","")

def str__f(f):
    n = int(f)
    r = f - n
    
    return str([str(n),str(abs(r))]).replace("'","")

def my_run(command, which_trial):
    print(*which_trial)
    print("\tcommand: %s"%command)
    subprocess.run(command, check=True)

# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    which_trial = (i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action, id_launcher, 
            strn(insole_start[i][0])[0], 
            strn(insole_start[i][0])[1], 
            str(timeout_time),
            str(angle),
            str(ik_delay),
            model_file,
            moment_arm_lib,
            str__f(insole_start[i][1]),
            str__f(insole_start[i][2]),
            str(clock_slowdown_rate),
            str(height/default_urdf_model_height),
            grf_no_rotation,
            ]

    try:
        # Use timeout_decorator.timeout to enforce timeout
        @timeout_decorator.timeout((timeout_time+ik_delay)*clock_slowdown_rate)  # N seconds timeout, but if there is a clock slowdown, then it will need proportionally a larger amount of time
        def run_subprocess():
            time.sleep(3) ## gives you time to kill this
            my_run(command,which_trial)

        if USE_TIMEOUT:
            run_subprocess()
        else:
            if i in trials_to_run: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                my_run(command,which_trial)
        #print("Bash script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("goodbye")
        break
    except timeout_decorator.TimeoutError:
        print("Bash script execution timed out.")
        cleanup_subprocesses()


source_directory="/tmp/04"

#for source_topic in ["/id_node/output","/so_rr_node/output_multi"]:

print("parsing bag files...")
for source_topic, bag_prefix in zip(["/so_rr_node/output_multi"],["so"]):
    for bag_file in glob.glob(source_directory+"/%s*.bag"%bag_prefix):
        p = subprocess.Popen(["rostopic","echo","-b", bag_file,"-p",source_topic], stdout=subprocess.PIPE) #> timings.txt])
        out, err = p.communicate()
        with open(bag_file+"_timings.txt", 'wb') as timings:
            timings.write(out)

print("copying data...")
base_directory = '/srv/host_data/tmp/04/'
new_directory_name = 'test_%s'%action
counter = 1

while True:
    directory_name = f"{new_directory_name}_{counter}"
    directory_path = os.path.join(base_directory, directory_name)
    
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        break
    
    counter += 1

bling(directory_path)
#copy sample analysis notebook

new_ipynb_name =os.path.join(directory_path, "%d_%s_analysis.ipynb"%(counter,action)) 

shutil.copy(sample_notebook, new_ipynb_name)

##lazy sed
subprocess.run(["sed", "-i", "s/ROT_STRING/%s/g"%rot_string, new_ipynb_name])
subprocess.run(["sed", "-i", "s/THIS_ACTION/%s/g"%action, new_ipynb_name])
subprocess.run(["sed", "-i", "s/weight= 54/weight= %f/g"%weight, new_ipynb_name])
subprocess.run(["sed", "-i", "s/subject_num=\"02\"/subject_num=\"%s\"/g"%subjectnum, new_ipynb_name])

#copy trials generated by this script to new folder we just created

# Loop through files in the source directory and move them to the destination.
for filename in os.listdir(source_directory):
    source_file = os.path.join(source_directory, filename)
    destination_file = os.path.join(directory_path, filename)
    shutil.move(source_file, destination_file)


refdata.merge_grfs.run(directory_path)


