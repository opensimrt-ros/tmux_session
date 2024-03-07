#!/usr/bin/env python3

import subprocess
import tkinter as tk
import rospy
from std_srvs.srv import Empty, EmptyResponse
from opensimrt_msgs.srv import LabelsSrv

class CommandButtonMulti(tk.Button):
    def __init__(self, text, service_handle_list, service_type_list):
        self.service_handle_list = service_handle_list
        super(CommandButtonMulti, self).__init__(text= text, command= self.send_command)
        self.pack()
        self.call = []
        for service_handle,service_type in zip(service_handle_list, service_type_list):
            self.call.append(rospy.ServiceProxy(service_handle, service_type))
    def send_command(self):
        for this_call in self.call:
            print(f"calling commands {this_call}")
            this_call()

class CommandButton(tk.Button):
    def __init__(self, text, service_handle, service_type):
        self.service_handle = service_handle
        super(CommandButton, self).__init__(text= text, command= self.send_command)
        self.pack()
        self.call = rospy.ServiceProxy(service_handle, service_type)
    def send_command(self):
        print(f"calling command {self.service_handle}")
        self.call()

class SessionPlaybackFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.Ca1 = CommandButton("calibrate ar",            "/ar/ik_upperbody_node/calibrate", Empty)
        self.Ca2 = CommandButton("labels ar",               "/ar/ik_upperbody_node/out_labels", LabelsSrv)
        self.Pa  = CommandButton("start recording ar",      "/ar/ik_upperbody_node/start_recording", Empty)
        self.Ci1 = CommandButton("calibrate imu",           "/imu/ik_upperbody_node/calibrate", Empty)
        self.Ci2 = CommandButton("labels imu",              "/imu/ik_upperbody_node/out_labels", LabelsSrv)
        self.Pi  = CommandButton("start recording imu",     "/imu/ik_upperbody_node/start_recording", Empty)
        self.CallBoth = CommandButtonMulti("start recording both", ["/ar/ik_upperbody_node/start_recording","/imu/ik_upperbody_node/start_recording",],[Empty, Empty])
        self.CallBothstop = CommandButtonMulti("stop recording both", ["/ar/ik_upperbody_node/stop_recording","/imu/ik_upperbody_node/stop_recording",],[Empty, Empty])
        self.CallBothstop = CommandButtonMulti("write sto both", ["/ar/ik_upperbody_node/write_sto","/imu/ik_upperbody_node/write_sto",],[Empty, Empty])
        self.submit = tk.Button(self, text="Close Session",command = self.send_close)
        self.submit.pack()
    def send_close(self):
        print("closing tmux")
        process = subprocess.Popen(['tmux', 'kill-session'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit()
        
if __name__ == "__main__":
    root = tk.Tk()
    rospy.init_node("session_ar_imu")
    root.title("Tmux session ar imu capture")
    root.geometry('200x1200+1400+0')
    SessionPlaybackFrame(root).pack(fill="both", expand=True)
    root.mainloop()


