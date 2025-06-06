#tracks mouse movement, clicks, and scrolls
from pynput import mouse
import os
import datetime
import time

class MouseTracker:
    def __init__(self, logfile="logs/mouse_log.txt"):
        self.logfile = logfile
        self.running = False
        self.listener = None
        self.last_move_time = 0  #to reduce log spam from constant movement

        #create logs folder
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)

    def on_move(self, x, y):
        #triggered when mouse moved
        now = time.time()
        #log movement every 2s
        if now - self.last_move_time > 2:
            self._log("Mouse moved")
            self.last_move_time = now

    def on_click(self, x, y, button, pressed):
        #triggered when mouse clicked
        if pressed:
            btn = "Left click" if button == mouse.Button.left else "Right click"
            self._log(f"{btn} at position")

    def on_scroll(self, x, y, dx, dy):
        #triggered when mouse scrolls the wheel
        direction = "up" if dy > 0 else "down"
        self._log(f"Scrolled {direction}")

    def _log(self, message):
        #write log timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.logfile, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def set_logfile(self, path):
        #update log file path
        self.logfile = path

    def start(self):
        #start the mouse in background
        if not self.running:
            self.running = True
            self.listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll
            )
            self.listener.start()
            print("[MouseTracker] Started")

    def stop(self):
        #stop the mouse
        if self.listener:
            self.listener.stop()
            print("[MouseTracker] Stopped")
        self.running = False
