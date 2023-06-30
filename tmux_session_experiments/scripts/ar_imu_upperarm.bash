#!/usr/bin/env bash
SESSION_NAME=ar_imu_combined

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(
"roslaunch tmux_session_experiments ik_upper_both.launch async_run:=true" 		
"rqt_plot"
"rosrun tmux_session_core session_playback.py"
)
#"rosservice call /inverse_kinematics_from_file/start" 
#"roslaunch opensimrt	id.launch" 

W2=(
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=talus_r" 	
)

W3=(
"roslaunch osrt_ros ik_lowerbody_inverted_pelvis.launch model_file:=/srv/data/gait1992/residual_reduction_algorithm/model_adjusted.osim"	
"roslaunch osrt_ros custom.launch"
"rosrun tmux_session_core session_commander.py"
)

create_tmux_window "$SESSION_NAME" "rviz_urdf" "${W1[@]}"
#create_tmux_window "$SESSION_NAME" "imu_calibs" "${W2[@]}"
#create_tmux_window "$SESSION_NAME" "ik_imus" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME

#tmux setw synchronize-panes on

