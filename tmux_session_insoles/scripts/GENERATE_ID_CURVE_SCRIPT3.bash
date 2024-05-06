#!/usr/bin/env bash
SESSION_NAME=insole_${SUBJECT_NUM}

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"
#ros_core_tmux_clock "$SESSION_NAME"

tmux set -g pane-border-status top

INSOLE_DATA_FILE=$1
STO_DATA_FILE=$2
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_1992_disabled_vis.osim
#MODEL_FILE=/srv/data/gait1992/model/model_generic.osim
#MODEL_FILE=/srv/host_data/02_ruoli/gait2392_simbody_RW.osim
ACTION_NUM=$3
SUBJECT_NUM=$4
ACTION=$5
ID_NODE_LAUNCH=$6
#GRF_ORIGIN_Z_OFFSET=0.075
GRF_ORIGIN_Z_OFFSET=0.0
#MOMENT_ARM_LIB=/catkin_opensim/devel/lib/Gait1992MomentArm
WRENCH_DELAY=0.0
IK_START_SECS=$(expr $EPOCHSECONDS + 4)
INSOLE_START_SECS=$(expr $7 + $IK_START_SECS)
INSOLE_START_NSECS=$8
INSOLE_START_TIME=${IK_START_SECS}.${INSOLE_START_NSECS}
IK_START_NSECS=0
#CLOCK_START_SECS=${10}
#CLOCK_START_NSECS=${11}
TIMEOUT_TIME=${9}
TIMEOUT_BAG_FILE_SAVE_TIME=$(expr $TIMEOUT_TIME - 10)
TIMEOUT_STO_SAVER_NODES=$(expr $TIMEOUT_TIME - 12)
NUM_PROC_SO=4
ANGLE=${10}
IK_DELAY=${11}
MODEL_FILE=${12}
MOMENT_ARM_LIB=${13}
## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.

#"roslaunch moticon_insoles play_ik.launch filename:=$IK_DATA_FILE --wait" 
W0=(
#"rosrun tf view_frames"
"roslaunch moticon_insoles insole_tfs.launch tf_prefix:=ik/"
"roslaunch osrt_ros t41.launch sto_file:=$STO_DATA_FILE start_at_secs:=$IK_START_SECS start_at_nsecs:=$IK_START_NSECS"
"roslaunch osrt_ros t42.launch run_as_service:=true parent_frame:=map"
"roslaunch osrt_ros t43.launch vis:=false"
#### These to show the skeleton
#"roslaunch osrt_ros t44.launch base_parent:=opensim_default_frame"
"roslaunch osrt_ros t44.launch"
"roslaunch osrt_ros t45.launch show_rviz:=false"
"sleep 0.1 ;roslaunch osrt_ros t46.launch bypass_heading_computation:=true heading_debug:=0 heading_offset:=$ANGLE visualise:=false wait_to_start:=false model_file:=$MODEL_FILE"
"roslaunch osrt_ros vis_ik.launch model_file:=$MODEL_FILE"
)

W1=(
#"roslaunch osrt_ros ${ID_NODE_LAUNCH} get_second_label:=false left_foot_tf_name:=left_cop_filtered right_foot_tf_name:=right_cop_filtered model_file:=$MODEL_FILE ik_delay:=${IK_DELAY} max_buffer_length:=1000 --wait" 
"roslaunch osrt_ros ${ID_NODE_LAUNCH} get_second_label:=false left_foot_tf_name:=left_cop_filtered right_foot_tf_name:=right_cop_filtered model_file:=$MODEL_FILE ik_delay:=${IK_DELAY} max_buffer_length:=1000 grf_no_rotation:=false --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=$INSOLE_DATA_FILE publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 foot_length:=0.2486 foot_width:=0.0902 grf_origin_z_offset:=$GRF_ORIGIN_Z_OFFSET start_time:=$INSOLE_START_TIME --wait" 
#"roslaunch moticon_insoles play_ik_2392.launch model_file:=$MODEL_FILE filename:=$IK_DATA_FILE start_at_secs:=$IK_START_SECS start_at_nsecs:=$IK_START_NSECS --wait" 
"roslaunch republisher republisher_insoles.launch wrench_delay:=$WRENCH_DELAY --wait" 
#"roslaunch republisher republisher_insoles.launch wrench_delay:=$WRENCH_DELAY ns:=/no_delay/ --wait" 
"roslaunch osrt_ros so_round_robin_filtered_multi.launch n_proc:=$NUM_PROC_SO model_file:=$MODEL_FILE moment_arm_library_path:=$MOMENT_ARM_LIB"
#"roslaunch custom_clock simpler_clock.launch start_at_secs:=$CLOCK_START_SECS start_at_nsecs:=$CLOCK_START_NSECS clock_step_microsseconds:=1000 slowdown_rate:=1" 
#"roswtf" 
)
W2=(
"rosbag record /so_rr_node/output_multi /tf /tf_static -O /tmp/${SUBJECT_NUM}/so_output_${ACTION}_${ACTION_NUM} --duration=${TIMEOUT_BAG_FILE_SAVE_TIME}"
"rosbag record /id_node/output -O /tmp/${SUBJECT_NUM}/id_output_${ACTION}_${ACTION_NUM} --duration=${TIMEOUT_BAG_FILE_SAVE_TIME}"
"rosservice call /id_node/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
"rosservice call /so_visualization/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
"rosservice call /id_node/start_recording --wait" 
"rosservice call /ik/out_labels --wait" 
"rosservice call /moticon_insoles/start_playback --wait" 
#this doesnt work because we havent set the end times properly in the nodes, so it will keep on publishing for a very long time
#"rosservice call /inverse_kinematics_from_file/start_at --wait; sleep 2; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"rosservice call /ik/inverse_kinematics_from_file/start_at --wait" 
#"rqt_graph " 
"rosservice call /so_visualization/start_recording --wait" 
)
W3=(
#"rosrun osrt_ros graph_tau_id_1992.bash" 
"rostopic hz /ik/output"
#"rostopic echo /so_rr_node/output_multi"
"rostopic list"
#"rostopic echo /ik/output"
#"rostopic echo /ik/output_filtered"
##"rostopic hz /left/insole"
#"rostopic echo /left/insole"
"rostopic echo /left/wrench_filtered"
#"rostopic echo /right/insole"
"rostopic echo /right/wrench_filtered"
"rostopic echo /no_delay/left/wrench_filtered"
#"rostopic echo /right/insole"
"rostopic echo /no_delay/right/wrench_filtered"
##"rostopic echo /id_node/debug_cop_left"
##"rostopic echo /id_node/debug_cop_right"
##"rostopic echo /id_node/debug_grf_left"
##"rostopic echo /id_node/debug_grf_right"
##"rostopic echo /id_node/debug_ik"
##"rosrun moticon_insoles graph_grfs_republished.bash --wait" 
##"sleep 4.1; rosrun tf view_frames"
)
W4=(
"roslaunch osrt_ros vis_so_rr_multi.launch model_file:=$MODEL_FILE "
"roslaunch osrt_ros vis_id.launch model_file:=$MODEL_FILE "
"#rosrun tmux_session_insoles g_ik.bash"
"#rosrun tmux_session_insoles g_grf.bash"
"#rosrun tmux_session_insoles g_cop.bash"
"#rosrun osrt_ros graph_iks_old_filtered.bash"
"sleep ${TIMEOUT_STO_SAVER_NODES}; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"sleep ${TIMEOUT_STO_SAVER_NODES}; rosservice call /so_visualization/stop_recording ; rosservice call /so_visualization/write_sto" 
)
W5=(

	)
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis2" 	"${W4[@]}"
create_tmux_window "$SESSION_NAME" "ik_nodes" "${W0[@]}"
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"
#create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME



