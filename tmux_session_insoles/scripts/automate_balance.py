import os
import subprocess
import time
import timeout_decorator
import glob
import time
# Define a list of parameter tuples
# INSOLE FILE, IK FILE
common_path ='/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2' 
#ik_list = glob.glob("%s/*balance*_ik_lower.sto"%common_path)
#ik_list.sort()
#insole_list = glob.glob("%s/balance*_header_corrected.txt"%common_path)
#insole_list.sort()
#parameter_tuples = []

#for insole_file. ik_file in zip(insole_list, ik_list):
#    parameter_tuples.append((insole_file. ik_file))
fff = [
 "2023-03-03-12-06-20balance0110_ik_lower.sto",
 "2023-03-03-12-08-28balance0211_ik_lower.sto",
 "2023-03-03-12-09-32balance0312_ik_lower.sto",
]
parameter_tuples = [
    ('%s/balance01_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[0]),"02"),
    ('%s/balance02_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[1]),"02"),
    ('%s/balance03_header_corrected.txt'%common_path, '%s/%s'%(common_path,fff[2]),"02"),
    #('value1b', 'value2b'),
]

action="balance"
def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
# Path to your bash script
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT.bash'

# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    print(i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action]

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
