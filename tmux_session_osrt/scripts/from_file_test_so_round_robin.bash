#!/usr/bin/env bash

SESSION_NAME=so_round_robin

source "`rospack find tmux_session_core`/common_functions.bash"
#ros_core_tmux_slow "$SESSION_NAME"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top

W1=(
"rostopic hz /so_rr_node/output_multi" 
"roslaunch osrt_ros so_round_robin_filtered_multi.launch" 
"roslaunch osrt_ros id_filtered.launch use_exact_sync:=true" 
"#roslaunch osrt_ros agrfm_as_grf.launch model_file:=/srv/data/gait1992/residual_reduction_algorithm/model_adjusted.osim" 
"roslaunch osrt_ros agrfm_filtered_as_grf.launch model_file:=/srv/data/gait1992/residual_reduction_algorithm/model_adjusted.osim" 
"roslaunch osrt_ros ik_bare_1992.launch simulation_loops:=1900 " 
"rosrun rqt_graph rqt_graph" 
"sleep 2; rosservice call /inverse_kinematics_from_file/start" 
"roslaunch osrt_ros vis_so_rr_multi.launch" 
)

create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME
