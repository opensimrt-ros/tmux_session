#!/usr/bin/env bash
cd ~
rqt_plot -e\
	/id_node/debug_cop_left/data[0] \
	/id_node/debug_cop_left/data[1] \
	/id_node/debug_cop_left/data[2] \
	/id_node/debug_cop_left/data[3] \
	/id_node/debug_cop_left/data[4] \
	/id_node/debug_cop_left/data[5] \
	/id_node/debug_cop_right/data[0] \
	/id_node/debug_cop_right/data[1] \
	/id_node/debug_cop_right/data[2] \
	/id_node/debug_cop_right/data[3] \
	/id_node/debug_cop_right/data[4] \
	/id_node/debug_cop_right/data[5] 
