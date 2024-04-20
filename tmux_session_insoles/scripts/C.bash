#!/usr/bin/env bash
SESSION_NAME=insole

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top

## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.
W1=(
"roslaunch osrt_ros id_async_filtered.launch get_second_label:=false left_foot_tf_name:=left_filtered right_foot_tf_name:=right_filtered model_file:=/srv/data/gait1992/model/model_generic.osim --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 --wait" 
"roslaunch moticon_insoles play_ik.launch filename:=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto --wait" 
"roslaunch republisher republisher_sync_insoles.launch wrench_delay:=0.15 debug_publish_zero_cop:=false debug_publish_fixed_force:=false --wait" 
)
W2=(
"rosservice call /ik/outlabels --wait" 
"sleep 3; rosservice call /moticon_insoles/start_playback --wait ; rosrun tf tf_monitor map calcn_r" 
"sleep 3; rosservice call /inverse_kinematics_from_file/start --wait " 
"rqt_graph " 
"sleep 2; rosservice call /id_node/start_recording --wait" 
"sleep 2; rosservice call /id_node/set_name_and_path \"{name: 's2_id_walking_filtered_', path: '/catkin_ws/tmp/02' }\" --wait" 
)
W3=(
"rosrun osrt_ros graph_tau_id_1992.bash" 
"#rostopic hz /ik/output"
"#rostopic echo /id_node/debug_cop_left"
"#rostopic echo /id_node/debug_cop_right"
"#rostopic echo /id_node/debug_grf_left"
"#rostopic echo /id_node/debug_grf_right"
"#rostopic echo /id_node/debug_ik"
"#rosrun moticon_insoles graph_grfs_republished.bash --wait" 
"#sleep 4.1; rosrun tf view_frames"
"rosbag record /id_node/output"
)
W4=(
"#rosrun tmux_session_insoles g_ik.bash"
"#rosrun tmux_session_insoles g_grf.bash"
"#rosrun tmux_session_insoles g_cop.bash"
"sleep 20; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
)
W5=(

	)
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"
create_tmux_window "$SESSION_NAME" "vis2" 	"${W4[@]}"
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME



