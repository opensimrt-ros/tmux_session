#!/usr/bin/env python3

import subprocess
import tkinter as tk
import rospy

class CloseTmuxButtonFrame(tk.Frame):
    def __init__(self, parent, session_name):
        tk.Frame.__init__(self, parent)
        self.session_name = session_name
        if self.session_name:
            self.close_commands =['tmux', 'kill-session', '-t', self.session_name]
        else:
            rospy.logwarn_once("I don't seem to have a session name. I will close some session, but not necessarily the one you want!")
            self.close_commands =['tmux', 'kill-session']


        self.submit = tk.Button(self, text="Close Session", height=150, width=150, command = self.send_close)
        self.submit.pack()
    def send_close(self):
        print("closing tmux")
        process = subprocess.Popen(self.close_commands,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit()

if __name__ == "__main__":
    rospy.init_node("close_button", anonymous=True)
    session_name = rospy.get_param("~session_name")
    root = tk.Tk()
    root.title("Tmux session: "+session_name)
    root.geometry('200x200+1600+0')
    CloseTmuxButtonFrame(root, session_name).pack(fill="both", expand=True)
    root.mainloop()


