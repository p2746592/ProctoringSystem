#detects copy/paste and scans logs for flagged action

import os
import datetime
from pynput import keyboard    #detect key combinations
import keyboard as kb          #check CTRL is held

class AlertDetector:
    def __init__(self, alert_callback=None):
        self.alert_callback = alert_callback  #to notify when an alert is triggered
        self.listener = None

    def start(self):
        #start listen keyboard actions
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        print("Alert detection started")

    def stop(self):
        #stop listen keyboard
        if self.listener:
            self.listener.stop()
        print("Alert detection stopped")

    def on_key_press(self, key):
        #detect combinations Ctrl+C | Ctrl+V
        try:
            key_str = key.char  #'c' | 'v'
        except AttributeError:
            key_str = str(key)

        #Ctrl+C
        if key_str == "c" and self.is_ctrl_pressed():
            self.trigger_alert("Copy action detected!")

        #Ctrl+V
        elif key_str == "v" and self.is_ctrl_pressed():
            self.trigger_alert("Paste action detected!")

    def is_ctrl_pressed(self):
        #check CTRL key is held
        return kb.is_pressed('ctrl')

    def trigger_alert(self, message):
        #alert event
        print(f"[ALERT] {message}")
        if self.alert_callback:
            self.alert_callback(message)

    def scan_logs_for_alerts(self, keywords, websites, keystrokes_file, websites_file, log_path):
        #scan log files for flagged keywords or visited websites if found
        def check_file(file_path, items, label):
            if not os.path.exists(file_path):
                return

            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()

                for line in lines:
                    for item in items:
                        if item.strip() and item.strip().lower() in line.lower():
                            alert_msg = f"[ALERT] Flagged {label} detected: \"{item.strip()}\""
                            print(alert_msg)
                            self.log_alert(alert_msg, log_path)
                            if self.alert_callback:
                                self.alert_callback(alert_msg)
            except Exception as e:
                print(f"[ERROR] Failed to scan {label} log: {e}")

        check_file(keystrokes_file, keywords, "keyword")
        check_file(websites_file, websites, "website")

    def log_alert(self, message, log_path):
        #alert log file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_path, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"[ERROR] Failed to log alert: {e}")
