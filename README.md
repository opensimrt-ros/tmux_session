# Tmux session packages

These are meant to organize a bit the tmux sessions we use to check different pipeline configurations and tests. 

Normally we would use just launch files, but given the number of nodes an necessity of checking debug output from different portions of the code, tmux sessions were easier to use. 

This creates the problem that now the tmux sessions are an additional layer to starting nodes and they were a bit disorganized. These packages aim to make this a bit better. Ideally we would only use launch files and somehow separate their output in tmux panes, but this would take considerable time to implement, so this intermediate solution was proposed


## TODO:

- go over individual files and make sure they run properly
- go over individual files and make sure they use the common functions (adds a button for closing the session, renames the windows for easier navigation reduces some of the boilerplate code, makes it easier to add or remove panes from each window, as the splits are now created automatically)
