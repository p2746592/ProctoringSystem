import tkinter as tk
from tkinter import ttk, simpledialog
import os, time, threading
from datetime import datetime

#monitoring components
from keystroke import KeystrokeLogger
from screenshots import ScreenshotCapture
from mouse_tracker import MouseTracker
from websites import WebsiteTracker
from pdf_report import generate_pdf_from_txt
from encryption import encrypt_file

class ProctorStatusPage(tk.Frame):
    def __init__(self, parent, proctor_id):
        super().__init__(parent, bg="white")
        self.proctor_id = proctor_id

        #monitoring state
        self.monitoring = False
        self.session_name = ""
        self.session_start_time = None
        self.session_dir = None

        #live counts
        self.keystroke_count = 0
        self.screenshot_count = 0
        self.alert_count = 0
        self.website_count = 0

        #default preferences
        self.screenshot_interval = 3
        self.flagged_keywords = ["password", "cheat", "answer"]
        self.flagged_websites = ["chatgpt", "google"]

        #trackers
        self.keylogger = KeystrokeLogger(on_key_press=self.increment_keystrokes)
        self.screenshot_capture = None
        self.mouse_tracker = MouseTracker()
        self.website_tracker = WebsiteTracker(on_website_change=self.increment_websites)

        #log scanning
        self.last_scanned_keystroke_line = 0
        self.last_scanned_website_line = 0

        #UI setup
        self.setup_ui()

        #live updates
        self.after(1000, self.update_stats_display)

    def setup_ui(self):
        tk.Label(self, text=f"Proctor Dashboard: {self.proctor_id}", font=("Helvetica", 18, "bold"), bg="white").pack(pady=10)

        control_frame = tk.Frame(self, bg="white")
        control_frame.pack(pady=5)

        self.toggle_button = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.toggle_button.grid(row=0, column=0, padx=10)

        self.status_canvas = tk.Canvas(control_frame, width=26, height=26, bg="white", highlightthickness=0)
        self.status_canvas.grid(row=0, column=1)
        self.toggle_circle = self.status_canvas.create_oval(3, 3, 23, 23, fill="red", outline="black")

        self.status_label = tk.Label(control_frame, text="OFFLINE", font=("Helvetica", 12), fg="red", bg="white")
        self.status_label.grid(row=0, column=2, padx=10)

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(pady=20)

        self.table = ttk.Treeview(
            table_frame,
            columns=("pc", "status", "screenshots", "keystrokes", "websites", "alerts"),
            show="headings", height=6
        )
        self.table.pack()

        #column labels
        headers = {
            "pc": "PC",
            "status": "Status",
            "screenshots": "Screenshots (Live)",
            "keystrokes": "Keystrokes (Live)",
            "websites": "Websites (Live)",
            "alerts": "Alerts (Live)"
        }
        for col in self.table["columns"]:
            self.table.heading(col, text=headers[col])
            self.table.column(col, anchor="center", width=150)

        self.pc_id = self.table.insert("", "end", values=("PC1", "WAITING", "-", "-", "-", "-"))

    #count updates
    def increment_keystrokes(self): self.keystroke_count += 1
    def increment_screenshots(self, _): self.screenshot_count += 1
    def increment_websites(self, _): self.website_count += 1
    def increment_alerts(self, _): self.alert_count += 1

    #apply preference
    def update_settings(self, interval, keywords, websites):
        self.screenshot_interval = interval
        self.flagged_keywords = [k.strip().lower() for k in keywords if k.strip()]
        self.flagged_websites = [w.strip().lower() for w in websites if w.strip()]

    #start monitoring based on the current state
    def toggle_monitoring(self):
        self.monitoring = not self.monitoring

        if self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        #GUI change
        self.toggle_button.config(text="Stop Monitoring")
        self.status_canvas.itemconfig(self.toggle_circle, fill="green")
        self.status_label.config(text="ONLINE", fg="green")

        #reset counters
        self.keystroke_count = 0
        self.screenshot_count = 0
        self.alert_count = 0
        self.website_count = 0

        #create session folder structure
        title = simpledialog.askstring("Session Title", "Enter a name for this session:", parent=self)
        if not title:
            self.stop_monitoring(cancelled=True)
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_name = f"session_{title.strip().replace(' ', '_')}_{timestamp}"

        base_dir = os.path.join("C:/Users/Hp/OneDrive - De Montfort University/shared_report", self.proctor_id)
        self.session_dir = os.path.join(base_dir, self.session_name)
        self.pc_folder = os.path.join(self.session_dir, "PC1")

        os.makedirs(self.pc_folder, exist_ok=True)
        os.makedirs(os.path.join(self.pc_folder, "screenshots"), exist_ok=True)

        #file paths
        self.keystroke_path = os.path.join(self.pc_folder, "keystrokes.txt")
        self.websites_path = os.path.join(self.pc_folder, "websites.txt")
        self.alert_log_path = os.path.join(self.pc_folder, "alerts_log.txt")
        self.mouse_log_path = os.path.join(self.pc_folder, "mouse_log.txt")
        self.screenshots_log_path = os.path.join(self.pc_folder, "screenshots_log.txt")
        self.summary_path = os.path.join(self.pc_folder, "session_summary.txt")

        #configure trackers
        self.keylogger.set_logfile(self.keystroke_path)
        self.website_tracker.set_logfile(self.websites_path)
        self.mouse_tracker.set_logfile(self.mouse_log_path)

        self.screenshot_capture = ScreenshotCapture(
            interval=self.screenshot_interval,
            on_screenshot_taken=self.increment_screenshots
        )
        self.screenshot_capture.set_logfile(self.screenshots_log_path)
        self.screenshot_capture.screenshot_dir = os.path.join(self.pc_folder, "screenshots")

        #start threads
        self.keylogger.reset_count()
        threading.Thread(target=self.keylogger.start, daemon=True).start()
        threading.Thread(target=self.screenshot_capture.start, daemon=True).start()
        threading.Thread(target=self.website_tracker.start, daemon=True).start()
        threading.Thread(target=self.mouse_tracker.start, daemon=True).start()
        threading.Thread(target=self.continuously_scan_logs, daemon=True).start()

        self.session_start_time = datetime.now()

    def stop_monitoring(self, cancelled=False):
        #hsuts down all trackers and saves the session logs
        self.toggle_button.config(text="Start Monitoring")
        self.status_canvas.itemconfig(self.toggle_circle, fill="red")
        self.status_label.config(text="OFFLINE", fg="red")

        #stop all trackers
        for tracker in [self.keylogger, self.screenshot_capture, self.website_tracker, self.mouse_tracker]:
            try: tracker.stop()
            except: pass

        self.table.item(self.pc_id, values=("PC1", "DISCONNECTED", "-", "-", "-", "-"))

        #skip saving logs if user cancelled
        if cancelled or not self.session_start_time:
            return

        end_time = datetime.now()
        elapsed = str(end_time - self.session_start_time).split(".")[0]

        #save session summary
        try:
            with open(self.summary_path, "w") as f:
                f.write(f"PC NAME: PC1\nSESSION NAME: {self.session_name}\nPROCTOR ID: {self.proctor_id}\n")
                f.write(f"DATE: {self.session_start_time.strftime('%Y-%m-%d')}\n")
                f.write(f"START TIME: {self.session_start_time.strftime('%H:%M:%S')}\n")
                f.write(f"END TIME: {end_time.strftime('%H:%M:%S')}\n")
                f.write(f"ELAPSED TIME: {elapsed}\n")
                f.write(f"SCREENSHOTS COUNT: {self.screenshot_count}\n")
                f.write(f"KEYLOGS COUNT: {self.keystroke_count}\n")
                f.write(f"ALERTS COUNT: {self.alert_count}\n")
                f.write(f"WEBSITES COUNT: {self.website_count}\n")

            #generate PDF report
            generate_pdf_from_txt(self.pc_folder, os.path.join(self.pc_folder, "session_summary.pdf"))

            #encrypt logs
            for path in [self.keystroke_path, self.websites_path, self.alert_log_path, self.mouse_log_path, self.summary_path, self.screenshots_log_path]:
                encrypt_file(path)

        except Exception as e:
            print(f"[ERROR] Could not write session summary: {e}")

    def update_stats_display(self):
        #refresh the live counts
        if self.monitoring:
            self.table.item(self.pc_id, values=(
                "PC1",
                "CONNECTED",
                str(self.screenshot_count),
                str(self.keystroke_count),
                str(self.website_count),
                str(self.alert_count)
            ))
        self.after_id = self.after(1000, self.update_stats_display)

    def continuously_scan_logs(self):
        #scan logs every for keywords or suspicious sites
        while self.monitoring:
            self.scan_logs_for_alerts()
            time.sleep(5)

    def scan_logs_for_alerts(self):
        #searches keystroke and website logs for flagged items
        def scan_file(path, items, label, last_index_attr):
            if not os.path.exists(path): return
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                last_index = getattr(self, last_index_attr)
                new_lines = lines[last_index:]
                for line in new_lines:
                    for item in items:
                        if item.lower() in line.lower():
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            alert_msg = f"[{timestamp}] [{label.upper()} ALERT] \"{item}\" found in: {line.strip()}"
                            self.log_alert(alert_msg)
                            self.alert_count += 1

                setattr(self, last_index_attr, len(lines))
            except Exception as e:
                print(f"[ERROR] Scanning {label} log failed: {e}")

        scan_file(self.keystroke_path, self.flagged_keywords, "keyword", "last_scanned_keystroke_line")
        scan_file(self.websites_path, self.flagged_websites, "website", "last_scanned_website_line")

    def log_alert(self, message):
        #alerts to alert log file
        try:
            with open(self.alert_log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")
            print(f"[ALERT] {message}")
        except Exception as e:
            print(f"[ERROR] Failed to write alert: {e}")

