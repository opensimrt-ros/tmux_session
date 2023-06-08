#!/usr/bin/env bash
SESSION_NAME=imu_fixing

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux "$SESSION_NAME"

W1=(
"roslaunch gait1992_description human_control_imus_movable_pipeline.launch" 		
"rosrun rqt_reconfigure rqt_reconfigure" 					
"rosrun gait1992_description fixheading_server.py" 				
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

W3=(
"roslaunch osrt_ros ik_lowerbody_inverted_pelvis.launch"	
"roslaunch ximu3_ros ximu_lower.launch"
"roslaunch moticon_insoles onfeet_wrench.launch "
"roslaunch osrt_ros custom.launch"
"rosrun tmux_session_core session_commander.py"
)

create_tmux_window "$SESSION_NAME" "rviz_urdf" "${W1[@]}"
create_tmux_window "$SESSION_NAME" "imu_calibs" "${W2[@]}"
create_tmux_window "$SESSION_NAME" "ik_imus" 	"${W3[@]}"

tmux -2 a -t $SESSION_NAME

#tmux setw synchronize-panes on

