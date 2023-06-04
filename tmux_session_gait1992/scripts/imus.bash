#!/usr/bin/env bash
SESSION_NAME=imu_fixing

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

#"rviz -d /catkin_ws/_cam_tf.rviz" C-m
 #rviz -d ./_default.rviz
W1=(
 "roslaunch gait1992_description human_control_imus_movable.launch"
)
W2=(
 "roslaunch gait1992_description imu_fixer_group.launch body:=torso"  
 "roslaunch gait1992_description imu_fixer_group.launch body:=pelvis" 
 "roslaunch gait1992_description imu_fixer_group.launch body:=femur_l"
 "roslaunch gait1992_description imu_fixer_group.launch body:=femur_r"
 "roslaunch gait1992_description imu_fixer_group.launch body:=tibia_l"
 "roslaunch gait1992_description imu_fixer_group.launch body:=tibia_r"
 "roslaunch gait1992_description imu_fixer_group.launch body:=talus_l"
 "roslaunch gait1992_description imu_fixer_group.launch body:=talus_r"
)
#"rosservice call /inverse_kinematics_from_file/start" C-m
#"roslaunch opensimrt	id.launch" C-m

#"ls -la" C-m
W3=(
"rosrun rqt_reconfigure rqt_reconfigure"
)
#tmux setw synchronize-panes on
create_tmux_window "$SESSION_NAME" "my_window1" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "my_window2" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "my_window3" "${W3[@]}"

tmux -2 a -t $SESSION_NAME
