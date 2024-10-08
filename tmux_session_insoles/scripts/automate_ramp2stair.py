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

timeout_time = 60
#timeout_time = 80

sample_notebook="standard_analysis.ipynb"


common_path = "/srv/host_data/06_r_with_ramp/ViconData/Ruoli/Motion_Insole/RealTimeIkIDS2_ramp"
fff = ['2023-03-28-09-44-48ramp2stair011_ik_lower.sto',
 '2023-03-28-09-49-43ramp2stair022_ik_lower.sto',
 '2023-03-28-09-51-44ramp2stair033_ik_lower.sto',
 '2023-03-28-09-52-11ramp2stair044_ik_lower.sto',
 '2023-03-28-09-54-22ramp2stair055_ik_lower.sto',
 '2023-03-28-09-54-50ramp2stair066_ik_lower.sto',
 '~tmpB5_2023-03-28-09-49-43ramp2stair022_ik_lower.sto']
parameter_tuples = [
        ('%s/ramp2stair01_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[0]),'02'),
        ('%s/ramp2stair02_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[1]),'02'),
        ('%s/ramp2stair03_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[2]),'02'),
        ('%s/ramp2stair04_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[3]),'02'),
        ('%s/ramp2stair05_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[4]),'02'),
        ('%s/ramp2stair06_header_corrected.txt'%common_path,'%s/%s'%(common_path,fff[5]),'02')]
insole_start = [1679996688.133011,
	 1679996982.100011,
	 1679997103.1020112,
	 1679997129.604011,
	 1679997259.0200112,
	 1679997286.9770112]
ik_start = [(1679996688, 133011102),
	 (1679996983, 889728069),
	 (1679997104, 734781026),
	 (1679997131, 262083053),
	 (1679997262, 415745019),
	 (1679997290, 351881027)]
clock_start = [(1679996687, 0),
	 (1679996981, 0),
	 (1679997102, 0),
	 (1679997128, 0),
	 (1679997258, 0),
	 (1679997285, 0)]
action='ramp2stair'


id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"

def cleanup_subprocesses():
    subprocess.run(["tmux", "kill-session"])
    time.sleep(3)
# Path to your bash script
bash_script_path = 'GENERATE_ID_CURVE_SCRIPT.bash'



# Loop through the parameter tuples and run the subprocess
for i, (insole_file, ik_file, subjectnum) in enumerate(parameter_tuples):
    print(i, insole_file, ik_file)
    command = ['/opt/ros/noetic/bin/rosrun', 'tmux_session_insoles', bash_script_path, insole_file, ik_file, str(i), subjectnum, action, id_launcher, 
            str(insole_start[i]), 
            str(ik_start[i][0]), 
            str(ik_start[i][1]), 
            str(clock_start[i][0]), 
            str(clock_start[i][1]),
            str(timeout_time)
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


