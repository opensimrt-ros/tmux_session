#!/usr/bin/env bash
SESSION_NAME=insole

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top

START_TIME=$(expr $EPOCHSECONDS + 5)

NSECS=0
## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.
W1=(
"roslaunch osrt_ros id_async_filtered.launch get_second_label:=false left_foot_tf_name:=left_cop_filtered right_foot_tf_name:=right_cop_filtered model_file:=/srv/data/gait1992/model/model_generic.osim --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 foot_length:=0.3 foot_width:=0.1 start_time:=${START_TIME}.$NSECS use_synchronization_event:=true rsecs:=${START_TIME} rnsecs:=$NSECS rto:=8659037 lsecs:=${START_TIME}  lnsecs:=$NSECS lto:=8665572 --wait" 



"roslaunch moticon_insoles play_ik_2392.launch filename:=/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto model_file:=/srv/data/gait1992/model/model_generic.osim start_at_secs:=${START_TIME} start_at_nsecs:=$NSECS --wait" 
"roslaunch republisher republisher_insoles.launch wrench_delay:=0.1 debug_publish_zero_cop:=false debug_publish_fixed_force:=false --wait" 
"roslaunch osrt_ros so_round_robin_filtered_multi.launch n_proc:=4"
#"rostopic echo /id_node/output_multi"
)
W2=(
"rosservice call /ik/outlabels --wait" 
"sleep 3; rosservice call /moticon_insoles/start_playback --wait ; rosrun tf tf_monitor map calcn_r" 
"sleep 3; rosservice call /inverse_kinematics_from_file/start_at --wait " 
#"rqt_graph " 
"roslaunch osrt_ros vis_so_rr_multi.launch model_file:=/srv/data/gait1992/model/model_generic.osim"
)
W3=(
"sleep 2; rosservice call /id_node/start_recording --wait" 
"sleep 2; rosservice call /so_visualization/start_recording --wait" 
"sleep 2; rosservice call /id_node/set_name_and_path \"{name: 's2_id_walking_filtered_', path: '/catkin_ws/tmp/02' }\" --wait" 
"sleep 2; rosservice call /so_visualization/set_name_and_path \"{name: 's2_id_walking_filtered_', path: '/catkin_ws/tmp/02' }\" --wait" 
)
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME



