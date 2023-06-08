#!/usr/bin/env bash
SESSION_NAME=single_imu_lowerbody

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(
"roslaunch osrt_ros ik_lowerbody_inverted_pelvis.launch"
"roslaunch ximu3_ros ximu_as_pelvis.launch"
"roslaunch osrt_ros lower_body_tfs_pelvis.launch"
)
#"roslaunch osrt_ros agrfm.launch" 
#"roslaunch opensimrt_bridge ik_acceleration_prediction_gfrm.launch" 
#"rosrun rqt_graph rqt_graph" 
#"rosservice call /inverse_kinematics_from_file/start" 

#"cd /catkin_opensim/src/opensimrt_core/OpenSimRT/Pipeline; nv" 
#"cd /catkin_opensim/src/opensimrt_core/launch; nv" 

#"ls -la" 
#"ls -la" 
#tmux setw synchronize-panes on

create_tmux_window "$SESSION_NAME" "my_window1" "${W1[@]}"

tmux -2 a -t $SESSION_NAME


