#!/usr/bin/env python3

import subprocess
import tkinter as tk

class CloseTmuxButtonFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.submit = tk.Button(self, text="Close Session", height=150, width=150, command = self.send_close)
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
    root.title("Tmux session controller")
    root.geometry('200x200+1600+0')
    CloseTmuxButtonFrame(root).pack(fill="both", expand=True)
    root.mainloop()


