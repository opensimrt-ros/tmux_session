#!/usr/bin/env bash

tmux new-session -s mysession -d 
tmux set-option -s -t mysession default-command "bash --rcfile ~/.bashrc_ws.sh"
tmux send -t mysession:0.0 "roscore" C-m
sleep 2

tmux new-window
tmux new-window
tmux select-window -t 1
tmux split-window -h 
tmux split-window -h 
tmux split-window -h
tmux select-layout even-horizontal
tmux select-pane -t 3
tmux split-window -v -p 50 
tmux select-pane -t 2
tmux split-window -v -p 50 
tmux select-pane -t 1 
tmux split-window -v -p 50 
tmux select-pane -t 0
tmux split-window -v -p 50 

tmux send -t mysession:1.0 "sleep 2 ;roslaunch osrt_ros ik_lowerbody.launch" C-m
tmux send -t mysession:1.1 "roslaunch ximu3_ros ximu_lower.launch" C-m
tmux send -t mysession:1.2 "roslaunch ar_test acer_video_stream.launch" C-m
tmux send -t mysession:1.3 "ROS_NAMESPACE=usb_cam_acer rosrun image_proc image_proc" C-m
tmux send -t mysession:1.4 "rviz -d /catkin_ws/_cam_acer_tf.rviz" C-m
tmux send -t mysession:1.5 "rosrun osrt_ros graph_iks.bash" C-m
tmux send -t mysession:1.6 "roslaunch ar_test ar_cube_acer.launch" C-m

#tmux send -t mysession:1.2 "roslaunch osrt_ros id.launch" C-m
#tmux send -t mysession:1.3 "roslaunch osrt_ros agrfm.launch" C-m
#tmux send -t mysession:1.4 "roslaunch opensimrt_bridge ik_acceleration_prediction_gfrm.launch" C-m
#tmux send -t mysession:1.5 "rosrun rqt_graph rqt_graph" C-m
#tmux send -t mysession:1.6 "rosservice call /inverse_kinematics_from_file/start" C-m

#tmux send -t mysession:2.0 "cd /catkin_opensim/src/opensimrt_core/OpenSimRT/Pipeline; nv" C-m
#tmux send -t mysession:3.0 "cd /catkin_opensim/src/opensimrt_core/launch; nv" C-m

#tmux send -t mysession:1.6 "ls -la" C-m
#tmux send -t mysession:1.7 "ls -la" C-m
#tmux setw synchronize-panes on

tmux -2 a -t mysession
