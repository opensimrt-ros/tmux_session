#!/usr/bin/env bash
SESSION_NAME=insole_slow

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(
"rosparam set /use_sim_time true" 
"roslaunch osrt_ros id_filtered.launch get_second_label:=false left_foot_tf_name:=left right_foot_tf_name:=right" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt estimated_delay:=0.1" 
"roslaunch moticon_insoles play_ik.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto" 
 "rosrun moticon_insoles service_mux.py" 
"roslaunch custom_clock custom_clock.launch" 
"rostopic echo /clock" 
)

W2=(
"sleep 2; rosservice call /ik/outlabels" 
"sleep 3; rosservice call /moticon_insoles/start_playback" 
"sleep 3; rosservice call /inverse_kinematics_from_file/start" 
 "sleep 3; rosservice call /start_multi/trigger" 
"sleep 2.9; rosservice call /id_node/set_name_and_path \"{name: 's2_id_walking', path: '/tmp/s2' }\" " 
"rosbag record /id_node/output /left/force /right/force " 
	)

W3=(
 "rosrun osrt_ros graph_iks_old.bash" 
"rosrun osrt_ros graph_tau_id.bash" 
 "rostopic echo /id_node/output" 
 "rostopic echo /model_generic/joint_states" 
"rosrun osrt_ros graph_grfs.bash" 

	)

create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME

