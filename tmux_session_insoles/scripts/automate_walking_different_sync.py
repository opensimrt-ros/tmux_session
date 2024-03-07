#!/bin/env python3
import os
import subprocess
import time
import timeout_decorator
import glob
import time
import shutil

USE_TIMEOUT=True
#USE_TIMEOUT=False

timeout_time = 40
#timeout_time = 80

sample_notebook="standard_analysis.ipynb"
# Define a list of parameter tuples
# INSOLE FILE, IK FILE
common_path ='/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2' 
#ik_list = glob.glob("%s/*walking*_ik_lower.sto"%common_path)
#ik_list.sort()
#insole_list = glob.glob("%s/walking*_header_corrected.txt"%common_path)
#insole_list.sort()
#parameter_tuples = []

#for insole_file. ik_file in zip(insole_list, ik_list):
#    parameter_tuples.append((insole_file. ik_file))
fff = [
 "2023-03-03-11-53-52walking011_ik_lower.sto",
 "2023-03-03-11-56-24walking012_ik_lower.sto",
 "2023-03-03-11-56-54walking023_ik_lower.sto",
 "2023-03-03-11-57-09walking024_ik_lower.sto",
 "2023-03-03-11-57-52walking035_ik_lower.sto",
 "2023-03-03-11-58-11walking046_ik_lower.sto",
 "2023-03-03-11-58-32walking057_ik_lower.sto"
]
parameter_tuples = [
    ('%s/walking01_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[1]),"02"),
    ('%s/walking02_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[3]),"02"),
    ('%s/walking03_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[4]),"02"),
    ('%s/walking04_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[5]),"02"),
    ('%s/walking05_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[6]),"02"),
    #('value1b', 'value2b'),
]

insole_start = [1677844584.722696,
                1677844629.074165,
                1677844672.127696,
                1677844691.253696,
                1677844712.5966961]

## i mean they are actually strings
ik_start = [(1677844584, 722696065),
            (1677844629, "074165105"),
            (1677844672, 126554918),
            (1677844691, 259890995),
            (1677844712, 599657983)]

clock_start =[  (1677844581, 0),
                (1677844624, 0),
                (1677844669, 0),
                (1677844689, 0),
                (1677844709, 0)]

insole_diff = {
        "RSECS":1677844584,
        "RNSECS":992696065,
        "RT0":8659037,
        "LSECS":1677844584,
        "LNSECS":992696065,
        "LT0":8665572,
        }

action="walking"

id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"

def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
    time.sleep(3)
# Path to your bash script
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT2.bash'



# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    print(i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action, id_launcher, 
            str(insole_start[i]), 
            str(ik_start[i][0]), 
            str(ik_start[i][1]), 
            str(clock_start[i][0]), 
            str(clock_start[i][1]),
            str(timeout_time),
            str(insole_diff["RSECS"]),
            str(insole_diff["RNSECS"]),
            str(insole_diff["RT0"]),
            str(insole_diff["LSECS"]),
            str(insole_diff["LNSECS"]),
            str(insole_diff["LT0"]),
            ]

    try:
        # Use timeout_decorator.timeout to enforce timeout
        @timeout_decorator.timeout(timeout_time)  # N seconds timeout
        def run_subprocess():
            subprocess.run(command, check=True)

        if USE_TIMEOUT:
            run_subprocess()
        else:
            if i in [1]: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                subprocess.run(command, check=True)
        #print("Bash script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except timeout_decorator.TimeoutError:
        print("Bash script execution timed out.")
        cleanup_subprocesses()


source_directory="/tmp/02"

#for source_topic in ["/id_node/output","/so_rr_node/output_multi"]:
for source_topic in ["/so_rr_node/output_multi"]:
    for bag_file in glob.glob(source_directory+"/*.bag"):
        p = subprocess.Popen(["rostopic","echo","-b", bag_file,"-p",source_topic], stdout=subprocess.PIPE) #> timings.txt])
        out, err = p.communicate()
        with open(bag_file+"_timings.txt", 'wb') as timings:
            timings.write(out)

base_directory = '/catkin_ws/tmp/02/'
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

##instead of fixing the bug in opensimrt_core...
subprocess.run(["mv", "/tmp/*.sto", directory_path])
