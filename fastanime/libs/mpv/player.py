import tkinter as tk
from subprocess import Popen, PIPE
import os
import threading


class MPVPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("MPV Player Control")
        self.create_widgets()

        self.mpv_process = None
        self.mpv_thread = None

    def create_widgets(self):
        self.start_button = tk.Button(
            self.root, text="Start MPV", command=self.start_mpv
        )
        self.start_button.pack()

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause)
        self.pause_button.pack()

        self.play_button = tk.Button(self.root, text="Play", command=self.play)
        self.play_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop MPV", command=self.stop_mpv)
        self.stop_button.pack()

    def start_mpv(self):
        if self.mpv_process is None:
            self.mpv_thread = threading.Thread(target=self.run_mpv)
            self.mpv_thread.start()

    def run_mpv(self):
        self.mpv_process = Popen(
            ["mpv", "--input-ipc-server=/tmp/mpvsocket", "path/to/your/video.mp4"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            preexec_fn=os.setsid,
        )
        self.mpv_process.wait()
        self.mpv_process = None

    def send_command(self, command):
        if self.mpv_process:
            if not self.mpv_process.stdin:
                return
            self.mpv_process.stdin.write(f"{command}\n".encode("utf-8"))
            self.mpv_process.stdin.flush()

    def pause(self):
        self.send_command('{"command": ["set_property", "pause", true]}')

    def play(self):
        self.send_command('{"command": ["set_property", "pause", false]}')

    def stop_mpv(self):
        if self.mpv_process:
            self.send_command('{"command": ["quit"]}')
            self.mpv_process = None
            if not self.mpv_thread:
                return
            self.mpv_thread.join()


if __name__ == "__main__":
    root = tk.Tk()
    app = MPVPlayer(root)
    root.mainloop()
