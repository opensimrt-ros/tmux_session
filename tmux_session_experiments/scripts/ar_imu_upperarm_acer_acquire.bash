#!/usr/bin/env bash
SESSION_NAME=ar_imu_combined

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(

"rviz -d /catkin_ws/_cam_acer_tf.rviz" 
"roslaunch ar_test ar_acer_upperarm.launch" 
"roslaunch ar_test acer_video_stream.launch" 
"roslaunch osrt_ros ik_upper_both.launch " 
"roslaunch ximu3_ros ximu_upper.launch" 
"ROS_NAMESPACE=usb_cam_acer rosrun image_proc image_proc" 
)

create_tmux_window "$SESSION_NAME" "rviz_urdf" "${W1[@]}"
#create_tmux_window "$SESSION_NAME" "imu_calibs" "${W2[@]}"
#create_tmux_window "$SESSION_NAME" "ik_imus" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME

