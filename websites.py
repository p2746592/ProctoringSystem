#tracks active window title or browser URL

import pygetwindow as gw      # Detect current active window
import pyautogui              # Simulate key presses
import pyperclip              # Read from clipboard (extract URLs)
import os
import time
import datetime

class WebsiteTracker:
    def __init__(self, logfile="logs/websites.txt", interval=5, on_website_change=None):
        self.logfile = logfile
        self.interval = interval  #time between scans
        self.on_website_change = on_website_change  #callback (UI updates)
        self.last_window = None
        self.running = False

        #folder exists
        log_dir = os.path.dirname(self.logfile)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def start(self):
        #start tracking active windows in a loop
        self.running = True
        print("Website tracking started")
        while self.running:
            self.track_window()
            time.sleep(self.interval)

    def stop(self):
        #stop tracking
        self.running = False
        print("Website tracking stopped")

    def track_window(self):
        #check current active window and log
        active_window = gw.getActiveWindow()
        if not active_window:
            return

        window_title = active_window.title
        if window_title != self.last_window:
            self.last_window = window_title
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            #extract browser URL
            #url = self.extract_url_if_browser()
            #content = url if url else window_title
            content = window_title  # skip trying to extract URL

            self.log_website(content, timestamp)

            if self.on_website_change:
                self.on_website_change(content)

    def extract_url_if_browser(self):
        #try to copy browser URL using Ctrl+L > Ctrl+C
        try:
            pyautogui.hotkey('ctrl', 'l')  #focus address bar
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'c')  #copy URL
            time.sleep(0.1)
            url = pyperclip.paste()
            if url.startswith("http"):
                return url
        except Exception as e:
            print(f"[ERROR] URL extraction failed: {e}")
        return None

    def log_website(self, content, timestamp):
        #log website to file
        try:
            with open(self.logfile, "a") as f:
                f.write(f"[{timestamp}] {content}\n")
            print(f"[LOG] Window/URL: {content}")
        except Exception as e:
            print(f"[ERROR] Logging failed: {e}")

    def set_logfile(self, path):
        #update logs are written
        self.logfile = path
