#!/usr/bin/env bash
SESSION_NAME=insole

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top

## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.
INSOLE_DATA_FILE=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt
IK_DATA_FILE=/srv/host_data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto 
MODEL_FILE=/srv/host_data/02_ruoli/gait2392_simbody_RW.osim
MOMENT_ARM_LIB=/catkin_ws/devel/lib/Gait2392MomentArm_RW
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_1992_disabled_vis.osim
SUBJECT_NUM=02
ACTION=walking
ACTION_NUM=1
ID_NODE_LAUNCH=id_async_filtered_calcn_references.launch
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_19xx/model_generic19xx.osim


W1=(
"roslaunch osrt_ros ${ID_NODE_LAUNCH} get_second_label:=false left_foot_tf_name:=left_filtered right_foot_tf_name:=right_filtered model_file:=$MODEL_FILE --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=$INSOLE_DATA_FILE publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 foot_length:=0.2486 foot_width:=0.0902 --wait" 
"roslaunch moticon_insoles play_ik_2392.launch filename:=$IK_DATA_FILE --wait" 
"roslaunch republisher republisher_sync_insoles.launch wrench_delay:=0.1 debug_publish_zero_cop:=false debug_publish_fixed_force:=false --wait" 
"roslaunch osrt_ros so_round_robin_filtered_multi.launch n_proc:=4 model_file:=$MODEL_FILE moment_arm_library_path:=$MOMENT_ARM_LIB"
)
W2=(
"rosservice call /ik/outlabels --wait" 
"sleep 3; rosservice call /moticon_insoles/start_playback --wait ; rosrun tf tf_monitor map calcn_r" 
"sleep 3; rosservice call /inverse_kinematics_from_file/start --wait " 
"rqt_graph " 
"sleep 2; rosservice call /id_node/start_recording --wait" 
"sleep 2; rosservice call /so_visualization/start_recording --wait" 
"sleep 2; rosservice call /id_node/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
"sleep 2; rosservice call /so_visualization/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
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
#"rosbag record /id_node/output"
)
W4=(
"roslaunch osrt_ros vis_so_rr_multi.launch model_file:=$MODEL_FILE "
"#rosrun tmux_session_insoles g_ik.bash"
"#rosrun tmux_session_insoles g_grf.bash"
"#rosrun tmux_session_insoles g_cop.bash"
"sleep 20; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"sleep 20; rosservice call /so_visualization/stop_recording ; rosservice call /so_visualization/write_sto" 
)
W5=(

	)
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"
create_tmux_window "$SESSION_NAME" "vis2" 	"${W4[@]}"
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME




