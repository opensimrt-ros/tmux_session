#!/usr/bin/env python3

import subprocess
import tkinter as tk
import rospy
from std_srvs.srv import Empty, EmptyResponse


class SessionCommanderFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.calibrate = tk.Button(self, text="Calibrate", command = self.send_calibrate)
        self.calibrate.pack()
        self.submit = tk.Button(self, text="Close Session",command = self.send_close)
        self.submit.pack()
        self.call_calibrate = rospy.ServiceProxy("/ik_lowerbody_node/calibrate", Empty)
    def send_close(self):
        print("closing tmux")
        process = subprocess.Popen(['tmux', 'kill-session'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit()
    def send_calibrate(self):
        print("calling calibrate")
        self.call_calibrate()
        
if __name__ == "__main__":
    root = tk.Tk()
    rospy.init_node("session_commander")
    root.title("Tmux session comander")
    root.geometry('200x1200+1400+0')
    SessionCommanderFrame(root).pack(fill="both", expand=True)
    root.mainloop()


