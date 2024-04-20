#!/bin/env python3
import os
import subprocess
import time
import timeout_decorator
import glob
import time
import shutil

#USE_TIMEOUT=True
USE_TIMEOUT=False

timeout_time = 65
#timeout_time = 80

sample_notebook="standard_analysis.ipynb"


common_path = "/srv/host_data/06_r_with_ramp/ViconData/Ruoli/Motion_Insole/RealTimeIkIDS2_ramp"

fff = ['2023-03-28-10-01-07stair2ramp017_ik_lower.sto',
	 '2023-03-28-10-01-33stair2ramp028_ik_lower.sto',
	 '2023-03-28-10-01-55stair2ramp039_ik_lower.sto',
	 '2023-03-28-10-02-19stair2ramp0410_ik_lower.sto',
	 '2023-03-28-10-02-43stair2ramp0511_ik_lower.sto',
	 '2023-03-28-10-03-41stair2ramp0612_ik_lower.sto']
parameter_tuples = [
('%s/stair2ramp01_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[0]),'02'),
('%s/stair2ramp02_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[1]),'02'),
('%s/stair2ramp03_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[2]),'02'),
('%s/stair2ramp04_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[3]),'02'),
('%s/stair2ramp05_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[4]),'02'),
('%s/stair2ramp06_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[5]),'02'),
]

insole_start = [1679997667.395009,
	 1679997691.659009,
	 1679997715.182009,
	 1679997737.1830091,
	 1679997760.7160091,
	 1679997809.704009]
ik_start = [(1679997667, 395009040),
	 (1679997693, 21492004),
	 (1679997715, 955077886),
	 (1679997739, 383040904),
	 (1679997763, 913403987),
	 (1679997821, 288075923)]
clock_start = [(1679997666, 0),
	 (1679997690, 0),
	 (1679997714, 0),
	 (1679997736, 0),
	 (1679997759, 0),
	 (1679997808, 0)]

# So we assume that for each session the clocks of the insoles are running true. If not then each trial needs to be synchronized manually, this would mean a list of insole_diffs
# This is not a realistic fix though and only works on playback, we may also break the buffer from id while doing this if the delay is too large, since we need to fill the wrench buffer there, this may take quite a bit of fiddling.
insole_diff = {
        "RSECS":1679997667,
        "RNSECS":395009000,
        "RT0":7066418,
        "LSECS":1679997667,
        "LNSECS":395009000,
        "LT0":7047053,
        }
action='stair2ramp'

id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"

def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
    time.sleep(3)
# Path to your bash script
#bash_script_path = 'GENERATE_ID_CURVE_SCRIPT.bash'
bash_script_path = 'HENERATE_ID_CURVE_SCRIPT.bash'



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
            if i in [5]: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                subprocess.run(command, check=True)
        #print("Bash script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except timeout_decorator.TimeoutError:
        print("Bash script execution timed out.")
        cleanup_subprocesses()



source_directory="/tmp/02"

for bag_file in glob.glob(source_directory+"/*.bag"):
    p = subprocess.Popen(["rostopic","echo","-b", bag_file,"-p","/id_node/output"], stdout=subprocess.PIPE) #> timings.txt])
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


