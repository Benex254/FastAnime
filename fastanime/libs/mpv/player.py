import os
import shutil
import threading
from subprocess import DEVNULL, PIPE, Popen


class MPVPlayer:
    def __init__(self):
        self.mpv_process = None
        self.mpv_thread = None

    def start_mpv(self):
        if self.mpv_process is None:
            self.mpv_thread = threading.Thread(target=self.run_mpv)
            self.mpv_thread.start()

    def run_mpv(self, url):
        mpv = shutil.which("mpv")
        if mpv:
            self.mpv_process = Popen(
                [mpv, "--input-ipc-server=/tmp/mpvsocket", "--osc", url],
                stdin=PIPE,
                stdout=DEVNULL,
                stderr=DEVNULL,
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


mpv_player = MPVPlayer()
