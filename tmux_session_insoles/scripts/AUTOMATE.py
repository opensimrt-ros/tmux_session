#!/bin/env python3
##TODO: maybe I want to move this to refdata
import os, sys
import subprocess
import time
import timeout_decorator
import glob
import shutil
import rospkg
from multiprocessing import Process
import acquisition_of_raw_data.tmux_session_manager as tm
import rospy
import yaml
from opensimrt_msgs.srv import SetFileNameSrv, SetFileNameSrvResponse, SetFileNameSrvRequest

rospack = rospkg.RosPack()
tsc_pkg_path = rospack.get_path("tmux_session_core")
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
    subprocess.run(["tmux", "kill-session"]) #this is blocking so we dont need to wait
# Path to your bash script

def strn(f):
    n = int(f)
    r = f - n
    return str(n),str(abs(r)).replace("0.","")

def as_list(f):
    n = int(f)
    r = f - n
    
    return [n, r]

def str__f(f):
    n = int(f)
    r = f - n
    
    return str([str(n),str(abs(r))]).replace("'","")

def set_names_srv(num):
    id_node_srv ="/id_node/set_name_and_path" 
    so_node_srv ="/so_visualization/set_name_and_path"
    set_names_srv_id_node = rospy.ServiceProxy(id_node_srv,SetFileNameSrv)
    set_names_srv_so_node = rospy.ServiceProxy(so_node_srv,SetFileNameSrv)
    srv_msg = SetFileNameSrvRequest()
    srv_msg.name = f"s_{subjectnum:02}_walking_filtered_SCRIPT{num}_"
    srv_msg.path = f"/tmp/{subjectnum:02}"
    
    rospy.wait_for_service(id_node_srv)
    set_names_srv_id_node(srv_msg)
    rospy.wait_for_service(so_node_srv)
    set_names_srv_so_node(srv_msg)

import rosgraph

def my_run2(command_dic, which_trial):
    print(*which_trial)
    this_m = tm.TmuxManager("insole_%s"%subjectnum)
    this_m.create_session(initial_command="roscore")
    #print(command_dic)
    while(True):
        try:
            if rosgraph.is_master_online():
                ## here we may want to set the variable for artificial clock before any other node starts
                if not clock_slowdown_rate == 1:
                    rospy.set_param("/use_sim_time", True)
                break
        except:
            rospy.sleep(0.1)

    rospy.init_node("trials_to_run")
    p = Process(target= set_names_srv, args=(i,))
    p.start()
    #set params manually because we don't know how to do it otherwise
    rospy.set_param("/moticon_insoles/diff_time",diff_time_dict)
    

    timediff_yaml = os.path.join(directory_path, "time_diff%s.yaml"%replace_strings_dict["$ACTION_NUM"]) 
    with open(timediff_yaml, 'w') as outfile:
        yaml.dump(diff_time_dict, outfile, default_flow_style=False, sort_keys=False)

    tm.create_some_windows(window_dic=command_dic,some_manager=this_m)
    #time.sleep(1)
    this_m.attach()
    p.join()
    #this_m.attach()  we want to show things, right?

def add_curly_braces_to_string(s):
    return    s.replace("$","${")+"}"

packages_to_check = [
        "tmux_session_insoles",
        "osrt_ros",
        "opensimrt"
        ]

def create_packages_rev_parse_strings(package_list):
    revparse_dic = {}
    for package in package_list:
        this_package_path = rospack.get_path(package)
        print(this_package_path)
        this_git_rev = subprocess.check_output(["/usr/bin/git","rev-parse","HEAD"],cwd=this_package_path).decode("ascii").strip() # i need to change dirs or something
        revparse_dic.update({package:(this_package_path,this_git_rev)})
    return revparse_dic

## This assumes that you are not actively editing and commiting while this script is running.

##TODO: this no longer works when i mount a part of the submodules, so inside the docker none of this is accessible. it isnt a big deal, you can still push things from the outside, but it may be a bit more cumbersome. 

#revparse_dic = create_packages_rev_parse_strings(packages_to_check)

revparse_dic ={"NOTICE":"this is no longer working. fix submodules .git and .gitmodules references to be links and do not mount the thing that they are linked to, but instead create an appropriate one inside the docker and keep the correct one outside of it. it will be a pain to keep working with submodules, you will definitely need a custom script to clone this."}

###### COMMON trial variables

#USE_TIMEOUT=True
USE_TIMEOUT=False

#trials_to_run = [0,1,2,3,4,5,6,7,8]
trials_to_run = [3]

num_so_threads = 4

clock_slowdown_rate= 1
#clock_slowdown_rate=10

timeout_time = 20
#timeout_time = 80
trial_ctr_c_time = 1

#show_rviz = True
show_rviz = False ## default

with_rotation = True
#with_rotation = False

## eh? a for loop?
subjectnum = 4
action="walking"
default_urdf_model_height=1.75 #???
##we have to scale the urdf model...

id_ik_delay=5.0 ## this is the id_ik_delay for ID

id_launcher="id_async_filtered.launch"
#id_launcher="id_async_filtered_calcn_references.launch"

## the ik will always start at like epoch+3

# insole_start  is the time difference between them as sec, .secs (it's going to be appended)

#it's like each line is a trial
#
# then the first element of the tuple is the common insole delay and the second and third are
#insole left , insole right
#

##this is from trying with point_x

## this is will be subtracted to insole delay to make it possible to make insoles go faster than ik. value in seconds
#insole_starts_sooner = 1.1
insole_starts_sooner = 1.0 ## one is the normal value since we are adding it alway to insole_start and this will subtract the delay
ik_start_delay = 6


subject_list = [4]
action_list = ["walking"]

if with_rotation:
    grf_no_rotation = "false"
    rot_string = "with rotation"
else:
    grf_no_rotation = "true" ## we used it the other way around...
    rot_string = "WITHOUT rotation"

for subjectnum in subject_list:
    base_directory = f'/srv/host_data/tmp/{subjectnum:02}/'
    source_directory=f"/tmp/{subjectnum:02}"
    if not os.path.exists(source_directory):
        os.makedirs(source_directory)
    with open("subjects/%02d.yaml"%subjectnum,"r") as a: 
        this_subject = yaml.load(a, Loader=yaml.loader.Loader)
    for action in action_list:
        if action == "other_action":
            continue
        new_directory_name = 'test_%s'%action



        counter = 333

        while True:
            directory_name = f"{new_directory_name}_{counter}"
            directory_path = os.path.join(base_directory, directory_name)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                break
            counter += 1



        bling(directory_path)

## stores also the git rev-parse of every package:


        git_state_yaml = os.path.join(directory_path, "git_packages_state.yaml") 
        with open(git_state_yaml, 'w') as outfile:
            yaml.dump(revparse_dic, outfile, default_flow_style=False, sort_keys=False)



        # Loop through the parameter tuples and run the subprocess
        for i, (insole_file, ik_file) in enumerate(zip(
            [os.path.join (this_subject["data_path"], insole_file_suffix) for insole_file_suffix in  this_subject["actions"][action]["insole_files"]],
            [os.path.join (this_subject["data_path"],imu_file_suffix) for imu_file_suffix in  this_subject["actions"][action]["imu_files"]]
            )):
            if USE_TIMEOUT:
                time.sleep(trial_ctr_c_time) ## gives you time to kill this
            which_trial = (i, insole_file, ik_file)
            epoch_time = int(time.time())
            ik_start_secs = epoch_time + ik_start_delay
            this_insole_start = ik_start_secs+this_subject["actions"][action]["insole_start"][i][0] - insole_starts_sooner
            real_timeout_time = (timeout_time+ik_start_delay+id_ik_delay)*clock_slowdown_rate + trial_ctr_c_time
            #We create a dictionary :
            replace_strings_dict = {
                    "$INSOLE_DATA_FILE":            insole_file,
                    "$STO_DATA_FILE":               ik_file,
                    "$ACTION_NUM":                  str(i),
                    "$SUBJECT_NUM":                 f"{subjectnum:02}",
                    "$ACTION":                      action,
                    "$ID_NODE_LAUNCH":              id_launcher,
                    "$INSOLE_START_NSECS":          strn(this_subject["actions"][action]["insole_start"][i][0])[1],
                    "$ANGLE":                       str(this_subject["base_imu_angle_offset"]),
                    "$IK_DELAY":                    str(id_ik_delay),
                    "$MODEL_FILE":                  this_subject["model_file"],
                    "$MOMENT_ARM_LIB":              this_subject["moment_arm_lib"],
                    "$INSOLE_START_DLEFT":          str__f(this_subject["actions"][action]["insole_start"][i][1]),
                    "$INSOLE_START_DRIGHT":         str__f(this_subject["actions"][action]["insole_start"][i][2]),
                    "$CLOCK_SLOWDOWN_RATE":         str(clock_slowdown_rate),
                    "$URDF_MODEL_SCALE":            str(this_subject["height"]/default_urdf_model_height),
                    "$GRF_NO_ROTATION":             grf_no_rotation,
                    "$GRF_ORIGIN_Z_OFFSET":         str(0.0),
                    "$WRENCH_DELAY":                str(0.0),
                    "$IK_START_NSECS":              str(0),
                    "$NUM_PROC_SO":                 str(num_so_threads),
                    "$CLOCK_START_SECS":            str(epoch_time),
                    "$CLOCK_START_NSECS":           str(0),
                    "$SESSION_NAME":                "insole_%s"%subjectnum,
                    "$IK_START_SECS":               str(ik_start_secs),
                    "$INSOLE_START_TIME":           str(this_insole_start),
                    "$TIMEOUT_TIME":                str(real_timeout_time),
                    "$TIMEOUT_BAG_FILE_SAVE_TIME":  str(real_timeout_time - 12),
                    "$TIMEOUT_STO_SAVER_NODES":     str(real_timeout_time - 12),
                    "$SHOW_RVIZ":                   str(show_rviz),
                    "$SHOW_VIZ_OTHER":              "false",
                    }

            diff_time_dict = {
                    'left':as_list(this_subject["actions"][action]["insole_start"][i][1]),
                    'right':as_list(this_subject["actions"][action]["insole_start"][i][2]),
                    }

            ##TODO: only save if we run it
            commands_yaml = os.path.join(directory_path, "tmux_execute%d.yaml"%i) 
            if USE_TIMEOUT or i in trials_to_run: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                with open(os.path.join(tsi_pkg_path, "config","GEN.yaml.template"), "rt") as fin:

                      ##if i in   
                    with open(commands_yaml, "wt") as fout:
                        for line in fin:
                            for key, val in replace_strings_dict.items():
                                #print(val)
                                line = line.replace(add_curly_braces_to_string(key), val)
                                line = line.replace(key, val)
                            fout.write(line)
                ## now run the yaml
                startup_dic = {}    
                with open(commands_yaml) as stream:
                    try:
                        startup_dic = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print("failed at trial %d"%i )
                        print(exc)
                        exit(1)
            def normal_run():
                #p = subprocess.Popen([os.path.join(tsc_pkg_path,"close_tmux_button.py")])
                my_run2(startup_dic,which_trial)
                #out, err = p.communicate() # this part is blocking

            if USE_TIMEOUT:
                try:
                    # Use timeout_decorator.timeout to enforce timeout
                    @timeout_decorator.timeout(real_timeout_time)  # N seconds timeout, but if there is a clock slowdown, then it will need proportionally a larger amount of time
                    def run_subprocess():
                        normal_run()
                    print(f"will close in {real_timeout_time} s")
                    run_subprocess()
                    #print("Bash script executed successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")
                except KeyboardInterrupt:
                    print("goodbye")
                    break
                except timeout_decorator.TimeoutError:
                    print("Bash script execution timed out.")
                finally:
                    cleanup_subprocesses()
            if not USE_TIMEOUT and i in trials_to_run: ## put the trials you want to check manually here and set USE_TIMEOUT to False
                normal_run()


#for source_topic in ["/id_node/output","/so_rr_node/output_multi"]:
        ##eh, note that this is dangerous because we specify the tmp directory per subject. I don't know if it will work well for multiple actions
        print("parsing bag files...")
        for source_topic, bag_prefix in zip(["/so_rr_node/output_multi"],["so"]):
            for bag_file in glob.glob(source_directory+"/%s*.bag"%bag_prefix):
                p = subprocess.Popen(["rostopic","echo","-b", bag_file,"-p",source_topic], stdout=subprocess.PIPE) #> timings.txt])
                out, err = p.communicate()
                with open(bag_file+"_timings.txt", 'wb') as timings:
                    timings.write(out)

        print("copying data...")
        #copy sample analysis notebook

        new_ipynb_name =os.path.join(directory_path, "%d_%s_analysis.ipynb"%(counter,action)) 

        shutil.copy(sample_notebook, new_ipynb_name)

        ##lazy sed
        subprocess.run(["sed", "-i", "s/ROT_STRING/%s/g"%rot_string, new_ipynb_name])
        subprocess.run(["sed", "-i", "s/THIS_ACTION/%s/g"%action, new_ipynb_name])
        subprocess.run(["sed", "-i", "s/weight= 54/weight= %f/g"%this_subject["weight"], new_ipynb_name])
        subprocess.run(["sed", "-i", "s/subject_num=\"02\"/subject_num=\"%s\"/g"%subjectnum, new_ipynb_name])

        #copy trials generated by this script to new folder we just created

        # Loop through files in the source directory and move them to the destination.
        for filename in os.listdir(source_directory):
            source_file = os.path.join(source_directory, filename)
            destination_file = os.path.join(directory_path, filename)
            ##hopefully this makes sure that we are left with no tmp files after each action. should be confirmed with the break below
            shutil.move(source_file, destination_file)


        refdata.merge_grfs.run(directory_path)

        exit()


