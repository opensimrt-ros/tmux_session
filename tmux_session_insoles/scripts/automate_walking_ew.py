#!/bin/env python3
import os
import subprocess
import time
import timeout_decorator
import glob
import time
import shutil
import rospkg
rospack = rospkg.RosPack()

tsi_pkg_path = rospack.get_path("tmux_session_insoles")

#USE_TIMEOUT=True
USE_TIMEOUT=False

trials_to_run = [8]
clock_slowdown_rate= 1

#clock_slowdown_rate= 1

timeout_time = 30
#timeout_time = 80

sample_notebook=os.path.join(tsi_pkg_path, "scripts", "standard_analysis.ipynb")
# Define a list of parameter tuples
# INSOLE FILE, IK FILE
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
# then the first element of the tuple is the common ik delay and the second and third are
#insole left , insole right
#

insole_start = [([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ]),
                ([0, 0  ],[0, 0  ],[0, 0  ])]

ik_delay=3.0

action="walking"

id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"

def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
    time.sleep(3)
# Path to your bash script
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT3.bash'

angle=-60.87

# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    print(i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action, id_launcher, 
            str(insole_start[i][0][0]), 
            str(insole_start[i][0][1]), 
            str(timeout_time),
            str(angle),
            str(ik_delay),
            model_file,
            moment_arm_lib,
            str(insole_start[i][1]),
            str(insole_start[i][2]),
            str(clock_slowdown_rate),
            ]

    try:
        # Use timeout_decorator.timeout to enforce timeout
        @timeout_decorator.timeout((timeout_time+ik_delay)*clock_slowdown_rate)  # N seconds timeout, but if there is a clock slowdown, then it will need proportionally a larger amount of time
        def run_subprocess():
            subprocess.run(command, check=True)

        if USE_TIMEOUT:
            run_subprocess()
        else:
            if i in trials_to_run: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                subprocess.run(command, check=True)
        #print("Bash script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except timeout_decorator.TimeoutError:
        print("Bash script execution timed out.")
        cleanup_subprocesses()


source_directory="/tmp/04"

#for source_topic in ["/id_node/output","/so_rr_node/output_multi"]:
for source_topic in ["/so_rr_node/output_multi"]:
    for bag_file in glob.glob(source_directory+"/*.bag"):
        p = subprocess.Popen(["rostopic","echo","-b", bag_file,"-p",source_topic], stdout=subprocess.PIPE) #> timings.txt])
        out, err = p.communicate()
        with open(bag_file+"_timings.txt", 'wb') as timings:
            timings.write(out)

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

print(directory_path)
#copy sample analysis notebook

new_ipynb_name =os.path.join(directory_path, "%s_analysis.ipynb"%action) 

shutil.copy(sample_notebook, new_ipynb_name)

##lazy sed
subprocess.run(["sed", "-i", "s/THIS_ACTION/%s/g"%action, new_ipynb_name])

#copy trials generated by this script to new folder we just created

# Loop through files in the source directory and move them to the destination.
for filename in os.listdir(source_directory):
    source_file = os.path.join(source_directory, filename)
    destination_file = os.path.join(directory_path, filename)
    shutil.move(source_file, destination_file)
