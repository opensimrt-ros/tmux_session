#!/usr/bin/env bash
SESSION_NAME=insole

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux_clock "$SESSION_NAME"

tmux set -g pane-border-status top

## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.
INSOLE_DATA_FILE=/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/walking01_header_corrected.txt
IK_DATA_FILE=/catkin_ws/Data/ruoli/ViconData/Ruoli/Moticon_insole/RealTimekIDS2/2023-03-03-11-56-24walking012_ik_lower.sto 
MODEL_FILE=/catkin_ws/Data/02_ruoli/gait2392_simbody_RW.osim
MOMENT_ARM_LIB=/catkin_ws/devel/lib/Gait2392MomentArm_RW
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_1992_disabled_vis.osim
#MODEL_FILE=/catkin_ws/src/gait1992_description/models/model_generic_19xx/model_generic19xx.osim
ACTION_NUM=1
SUBJECT_NUM=2
ACTION=walking
WRENCH_DELAY=0.14
INSOLE_START_TIME=1677844584.722696
IK_START_SECS=1677844584
IK_START_NSECS=722696000
CLOCK_START_SECS=1677844580
CLOCK_START_NSECS=0
## it seems like we are messing up with the publish_transforms=false, but we are actually republishing the values using the combined message with everything from the insoles, so it is okay
## another caveat is that the insoles delay is being completely overlooked by the republisher node which has its own delay for publishing onld COP transforms, so we set it to zero. 
## looking at the transforms for the wrench in rviz will also be wrong because we publish transformations that are backstamped, so they will show it in a past robot that doesnt exist anymore.

W1=(
"roslaunch moticon_insoles play_ik_2392.launch model_file:=$MODEL_FILE filename:=$IK_DATA_FILE start_at_secs:=$IK_START_SECS start_at_nsecs:=$IK_START_NSECS --wait" 
"roslaunch moticon_insoles feet_wrench_and_ik_from_file.launch filename:=$INSOLE_DATA_FILE publish_transforms:=false output_left:=/grf_left/unfiltered output_right:=/grf_right/unfiltered estimated_delay:=0.0 foot_length:=0.2486 foot_width:=0.0902 grf_origin_z_offset:=$GRF_ORIGIN_Z_OFFSET start_time:=$INSOLE_START_TIME --wait" 
"roslaunch custom_clock back_in_time_clock.launch start_at_secs:=$CLOCK_START_SECS start_at_nsecs:=$CLOCK_START_NSECS slowdown_rate:=1" 
"roslaunch republisher republisher_sync_insoles.launch wrench_delay:=$WRENCH_DELAY debug_publish_zero_cop:=false debug_publish_fixed_force:=false --wait" 
"rqt_graph " 
)
W2=(
"rosservice call /moticon_insoles/start_playback --wait"
"rostopic echo /left/force"
"rostopic echo /right/force"
"rostopic echo /left/insole"
"rostopic echo /right/insole"
"rosservice call /ik/outlabels --wait" 
"rosservice call /inverse_kinematics_from_file/start_at --wait" 
)
W3=(
"rosrun moticon_insoles graph_grfs_republished.bash --wait"
)
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "sync" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "graph" "${W3[@]}"

tmux -2 a -t $SESSION_NAME



