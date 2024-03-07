#!/usr/bin/env bash
SESSION_NAME=ar_imu_combined

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

tmux set -g pane-border-status top

W1=(

"rviz -d /catkin_ws/_cam_acer_tf.rviz" 
"roslaunch ar_test ar_acer_upperarm.launch" 
"roslaunch ar_test acer_video_stream.launch" 
"roslaunch osrt_ros ik_upper_both.launch " 
"roslaunch ximu3_ros ximu_upper.launch" 
"ROS_NAMESPACE=usb_cam_acer rosrun image_proc image_proc" 
)

W2=(
	"rosrun tmux_session_core session_commander_ar_imu.py"
"#rosservice call /ar/ik_upperbody_node/set_name_and_path '' ''" 
"#rosservice call /imu/ik_upperbody_node/set_name_and_path '' ''"
)
create_tmux_window "$SESSION_NAME" "rviz_urdf" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "session" "${W2[@]}"
#create_tmux_window "$SESSION_NAME" "ik_imus" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME

