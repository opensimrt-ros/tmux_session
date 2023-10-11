!/usr/bin/env bash
SESSION_NAME=insole

source "`rospack find tmux_session_core`/common_functions.bash"
ros_core_tmux_clock "$SESSION_NAME"

tmux set -g pane-border-status top

CLOCK_START_SECS=1677844580
CLOCK_START_NSECS=0

W1=(
"roslaunch custom_clock back_in_time_clock.launch start_at_secs:=$CLOCK_START_SECS start_at_nsecs:=$CLOCK_START_NSECS slowdown_rate:=1" 
)
create_tmux_window "$SESSION_NAME" "main_nodes" "${W1[@]}"

tmux -2 a -t $SESSION_NAME



