import os
import subprocess
import time
import timeout_decorator
import glob
import time
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

action="walking"

#id_launcher="id_async_filtered.launch"
id_launcher="id_async_filtered_calcn_references.launch"

def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
# Path to your bash script
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT.bash'

# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    print(i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action, id_launcher]

    try:
        # Use timeout_decorator.timeout to enforce timeout
        @timeout_decorator.timeout(40)  # 40 seconds timeout
        def run_subprocess():
            subprocess.run(command, check=True)

        run_subprocess()
        print("Bash script executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except timeout_decorator.TimeoutError:
        print("Bash script execution timed out.")
        cleanup_subprocesses()
    time.sleep(3)
