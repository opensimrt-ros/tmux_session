#!/usr/bin/env bash
SESSION_NAME=insole_slow

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top


W1=(
"rosparam set /use_sim_time true" 
"roslaunch osrt_ros id_filtered.launch get_second_label:=false left_foot_tf_name:=left_filtered right_foot_tf_name:=right_filtered use_exact_sync:=false --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.2 --wait" 
"roslaunch moticon_insoles play_ik.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto --wait" 
"roslaunch republisher republisher_insoles.launch --wait" 
"rostopic echo /clock" 
)
W2=(
"rosservice call /ik/outlabels --wait" 
"# rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"sleep 4; rosservice call /moticon_insoles/start_playback --wait " 
"sleep 3; rosservice call /inverse_kinematics_from_file/start --wait " 
"rqt_graph " 
"sleep 3; rosservice call /id_node/start_recording --wait" 
"sleep 3; rosservice call /id_node/set_name_and_path \"{name: 's2_id_walking', path: '/tmp/s2' }\" --wait" 
)
W3=(
"rosrun osrt_ros graph_tau_id.bash" 
"rostopic hz /ik/output"
"rosrun moticon_insoles graph_grfs_republished.bash --wait" 
"sleep 4.1; rosrun tf view_frames"
""
)
W4=(
"rostopic echo /grf_left/wrench"
"rostopic echo /grf_right/wrench"
"rostopic echo /ik/output_filtered"
"roslaunch custom_clock custom_clock.launch slowdown_rate:=1" 
	)
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"
create_tmux_window "$SESSION_NAME" "topics" 	"${W4[@]}"

tmux -2 a -t $SESSION_NAME



