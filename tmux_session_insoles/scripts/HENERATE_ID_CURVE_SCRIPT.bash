#!/usr/bin/env bash
#####
# TRY TO SYNCHRONIZE WITH REPUBLISHER
#####
echo "RUNNING script with arguments:"
echo "$0 $@"
SESSION_NAME=insole_${SUBJECT_NUM}

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux_clock "$SESSION_NAME"

tmux set -g pane-border-status top

INSOLE_DATA_FILE=$1
IK_DATA_FILE=$2
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_1992_disabled_vis.osim
#MODEL_FILE=/srv/data/gait1992/model/model_generic.osim
MODEL_FILE=/catkin_ws/Data/02_ruoli/gait2392_simbody_RW.osim
ACTION_NUM=$3
SUBJECT_NUM=$4
ACTION=$5
ID_NODE_LAUNCH=$6
GRF_ORIGIN_Z_OFFSET=0.075
#MOMENT_ARM_LIB=/catkin_opensim/devel/lib/Gait1992MomentArm
MOMENT_ARM_LIB=/catkin_ws/devel/lib/Gait2392MomentArm_RW
WRENCH_DELAY=0.14
INSOLE_START_TIME=$7 
IK_START_SECS=$8
IK_START_NSECS=$9
CLOCK_START_SECS=${10}
CLOCK_START_NSECS=${11}
TIMEOUT_TIME=${12}
TIMEOUT_BAG_FILE_SAVE_TIME=$(expr $TIMEOUT_TIME - 10)
TIMEOUT_STO_SAVER_NODES=$(expr $TIMEOUT_TIME - 12)
INSOLE_DIFF_RIGHT_SECS=${13}
INSOLE_DIFF_RIGHT_NSECS=${14}
INSOLE_DIFF_RIGHT_T0=${15}
INSOLE_DIFF_LEFT_SECS=${16}
INSOLE_DIFF_LEFT_NSECS=${17}
INSOLE_DIFF_LEFT_T0=${18}
## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.

#"roslaunch moticon_insoles play_ik.launch filename:=$IK_DATA_FILE --wait" 

## There is quite a lot of time variation in the insole measurements, so we need a ton of delay before reading the IK
IK_DELAY=5.0
## we also need to make sure we keep enough samples to be able to synchronize them, but this will make each wrench finding take longer
MAX_BUFFER_LENGTH_ID_ASYNC=$(awk -v num="$IK_DELAY" 'BEGIN {print num * 100}')
echo "MAX_BUFFER_LENGTH_ID_ASYNC= ${MAX_BUFFER_LENGTH_ID_ASYNC}"
#exit
W1=(
"roslaunch osrt_ros ${ID_NODE_LAUNCH} get_second_label:=false left_foot_tf_name:=left_filtered right_foot_tf_name:=right_filtered model_file:=$MODEL_FILE max_buffer_length:=${MAX_BUFFER_LENGTH_ID_ASYNC} ik_delay:=${IK_DELAY} --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=$INSOLE_DATA_FILE publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 foot_length:=0.2486 foot_width:=0.0902 grf_origin_z_offset:=$GRF_ORIGIN_Z_OFFSET start_time:=$INSOLE_START_TIME --wait" 
"roslaunch moticon_insoles play_ik_2392.launch model_file:=$MODEL_FILE filename:=$IK_DATA_FILE start_at_secs:=$IK_START_SECS start_at_nsecs:=$IK_START_NSECS --wait" 
"roslaunch republisher republisher_time_corrected_insoles.launch wrench_delay:=$WRENCH_DELAY debug_publish_zero_cop:=false debug_publish_fixed_force:=false right_sync_time_secs:=${INSOLE_DIFF_RIGHT_SECS} right_sync_time_nsecs:=${INSOLE_DIFF_RIGHT_NSECS} right_insole_t0:=${INSOLE_DIFF_RIGHT_T0} left_sync_time_secs:=${INSOLE_DIFF_LEFT_SECS} left_sync_time_nsecs:=${INSOLE_DIFF_LEFT_NSECS} left_insole_t0:=${INSOLE_DIFF_LEFT_T0} --wait" 
"roslaunch osrt_ros so_round_robin_filtered_multi.launch n_proc:=4 model_file:=$MODEL_FILE moment_arm_library_path:=$MOMENT_ARM_LIB"
"roslaunch custom_clock simpler_clock.launch start_at_secs:=$CLOCK_START_SECS start_at_nsecs:=$CLOCK_START_NSECS clock_step_microsseconds:=1000 slowdown_rate:=1" 
"rostopic echo /right/insole"
"rostopic echo /left/insole"
#"roswtf" 
)
W2=(
"rosbag record /id_node/output -O /tmp/${SUBJECT_NUM}/id_output_${ACTION}_${ACTION_NUM} --duration=${TIMEOUT_BAG_FILE_SAVE_TIME}"
"rosservice call /id_node/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
"rosservice call /so_visualization/set_name_and_path \"{name: 's${SUBJECT_NUM}_id_${ACTION}_filtered_SCRIPT${ACTION_NUM}_', path: '/tmp/${SUBJECT_NUM}' }\" --wait" 
"rosservice call /id_node/start_recording --wait" 
"rosservice call /ik/outlabels --wait" 
"rosservice call /moticon_insoles/start_playback --wait" 
#this doesnt work because we havent set the end times properly in the nodes, so it will keep on publishing for a very long time
#"rosservice call /inverse_kinematics_from_file/start_at --wait; sleep 2; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"rosservice call /inverse_kinematics_from_file/start_at --wait" 
"rqt_graph " 
"rosservice call /so_visualization/start_recording --wait" 
)
W3=(
#"rosrun osrt_ros graph_tau_id_1992.bash" 
#"rostopic hz /ik/output"
"rostopic echo /ik/output"
"rostopic echo /ik/output_filtered"
#"rostopic hz /left/insole"
"rostopic echo /left/insole"
"rostopic echo /grf_left/wrench"
"rostopic echo /right/insole"
"rostopic echo /grf_right/wrench"
#"rostopic echo /id_node/debug_cop_left"
#"rostopic echo /id_node/debug_cop_right"
#"rostopic echo /id_node/debug_grf_left"
#"rostopic echo /id_node/debug_grf_right"
#"rostopic echo /id_node/debug_ik"
#"rosrun moticon_insoles graph_grfs_republished.bash --wait" 
#"sleep 4.1; rosrun tf view_frames"
)
W4=(
"roslaunch osrt_ros vis_so_rr_multi.launch model_file:=$MODEL_FILE "
"rosrun tmux_session_insoles g_ik.bash"
"rqt_plot -e /grf_right/wrench/wrench/force/y/ /grf_left/wrench/wrench/force/y/ #rosrun tmux_session_insoles g_grf.bash"
"#rosrun tmux_session_insoles g_cop.bash"
"#rosrun osrt_ros graph_iks_old_filtered.bash"
"sleep ${TIMEOUT_STO_SAVER_NODES}; rosservice call /id_node/stop_recording ; rosservice call /id_node/write_sto" 
"sleep ${TIMEOUT_STO_SAVER_NODES}; rosservice call /so_visualization/stop_recording ; rosservice call /so_visualization/write_sto" 
)
W5=(

	)
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "vis2" 	"${W4[@]}"
#create_tmux_window "$SESSION_NAME" "vis" 	"${W3[@]}"
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME



