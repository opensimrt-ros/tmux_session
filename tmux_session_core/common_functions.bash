#!/usr/bin/env bash

ros_core_tmux()
{
	local session="$1"
	tmux new-session -s $session -n "roscore" -d
	tmux set-option -s -t $session default-command "bash --rcfile ~.bashrc"
	tmux send -t $session:0.0 "roscore" C-m
	tmux split-window -h -t "$session"
	tmux send -t $session:0.1 "rosrun tmux_session_core close_tmux_button.py --wait" C-m
	#roscore ok?
	until rostopic list ; do sleep 0.1; done 
	#sleep 2 


}

create_tmux_window() {

	local session="$1"
	local window_name="$2"
	local commands=("${@:3}")

	tmux new-window -n "$window_name"

	local num_commands=${#commands[@]}
	local num_splits
	if (( num_commands <= 1 )); then
		num_splits=0
	else
		num_splits=$((num_commands - 1))
	fi

	for ((i=1; i<num_splits; i+=2)); do
		#echo	splitting horizontal
		tmux split-window -h -t "$session:$window_name"
	done  
	tmux select-layout -t "$session:$window_name" even-horizontal
	local pane_index=$((num_commands/2 -1))
	for ((i=0; i<num_splits; i+=2)); do
		#echo "should have split vertically"
		tmux select-pane -t "$session:$window_name.$pane_index"
		tmux split-window -v -t "$session:$window_name"
		((pane_index--))
	done

	local pane_index=0
	for command in "${commands[@]}"; do
		tmux send-keys -t "$session:$window_name.$pane_index" "$command" C-m
		((pane_index++))
	done

}


