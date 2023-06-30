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
        self.Ca = CommandButton("get labels ar", "/ar/ik/outlabels", LabelsSrv)
        self.Pa = CommandButton("Play ar", "/ar/ik/start", Empty)
        self.Ci = CommandButton("get labels imu", "/imu/ik/outlabels", LabelsSrv)
        self.Pi = CommandButton("Play imu", "/imu/ik/start", Empty)
        self.CallBoth = CommandButtonMulti("Play both", ["/ar/ik/start","/imu/ik/start",],[Empty, Empty])
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
    rospy.init_node("session_playback")
    root.title("Tmux session playback")
    root.geometry('200x1200+1400+0')
    SessionPlaybackFrame(root).pack(fill="both", expand=True)
    root.mainloop()


