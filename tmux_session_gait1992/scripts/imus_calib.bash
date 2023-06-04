#!/usr/bin/env bash
SESSION_NAME=imu_fixing

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(
"roslaunch gait1992_description human_control_imus_movable.launch" 		
"rosrun rqt_reconfigure rqt_reconfigure" 					
"rosrun gait1992_description fixheading_server.py" 				
"roslaunch gait1992_description pelvis_map_pose_fake_tf_publisher.launch" 	
)
#"rosservice call /inverse_kinematics_from_file/start" 
#"roslaunch opensimrt	id.launch" 

W2=(
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=torso" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=pelvis" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=femur_l" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=femur_r" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=tibia_l" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=tibia_r" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=talus_l" 	
"roslaunch gait1992_description imu_initial_pose_setter.launch body:=talus_r" 	
)

create_tmux_window "$SESSION_NAME" "my_window1" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "my_window2" "${W2[@]}"

tmux -2 a -t $SESSION_NAME

#tmux setw synchronize-panes on

