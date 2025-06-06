#proctors view and download reports from past sessions

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import zipfile
import tempfile
import fitz  #PyMuPDF for reading PDFs

class ReportsPage(tk.Frame):
    def __init__(self, parent, user_id):
        super().__init__(parent, bg="white")
        self.user_id = user_id

        #session reports are stored (OneDrive)
        self.logs_root = os.path.join(
            "C:/Users/Hp/OneDrive - De Montfort University/shared_report", self.user_id
        )

        #title
        tk.Label(self, text="Reports Monitoring", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

        #reports table
        columns = ("session", "Keystroke Entries", "websites", "Captured Screenshots", "alerts")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=12, selectmode="browse")
        self.table.pack(fill="both", expand=True, padx=20)

        for col in columns:
            self.table.heading(col, text=col.capitalize())
            self.table.column(col, width=100 if col != "session" else 160, anchor="center")

        #load session data
        self.load_sessions()

        #buttons for Send & Download
        ttk.Button(self, text="Send Selected Reports", command=self.send_selected_reports).pack(pady=10)
        ttk.Button(self, text="Download Screenshots & PDF", command=self.download_selected_sessions).pack(pady=5)

    def load_sessions(self):
        #loads available sessions and displays stats
        self.table.delete(*self.table.get_children())

        if not os.path.exists(self.logs_root):
            return

        sessions = [d for d in os.listdir(self.logs_root) if os.path.isdir(os.path.join(self.logs_root, d))]
        sessions.sort()

        for session_name in sessions:
            session_path = os.path.join(self.logs_root, session_name)
            stats = self.get_log_stats(session_path)

            #clean session name for display
            display_name = session_name.replace("session_", "")
            if "_" in display_name:
                display_name = "_".join(display_name.split("_")[:-2])  # remove date/time suffix

            #add row to table
            self.table.insert("", "end", iid=session_name, values=(
                display_name,
                stats["keystrokes"],
                stats["websites"],
                stats["screenshots"],
                stats["alerts"]
            ))

    def get_log_stats(self, session_path):
        #reads first page of summary PDF and extracts log counts
        pc_folders = [f for f in os.listdir(session_path) if os.path.isdir(os.path.join(session_path, f))]
        if not pc_folders:
            return {"keystrokes": 0, "websites": 0, "screenshots": 0, "alerts": 0}

        pc_path = os.path.join(session_path, pc_folders[0])
        pdf_path = os.path.join(pc_path, "session_summary.pdf")

        if not os.path.exists(pdf_path):
            return {"keystrokes": 0, "websites": 0, "screenshots": 0, "alerts": 0}

        try:
            doc = fitz.open(pdf_path)
            text = doc[0].get_text()
            doc.close()

            #to extract "LABEL: number"
            def extract_count(label):
                for line in text.splitlines():
                    if line.strip().startswith(label):
                        parts = line.split(":")
                        if len(parts) == 2:
                            return int(parts[1].strip())
                return 0

            return {
                "keystrokes": extract_count("KEYLOGS COUNT"),
                "websites": extract_count("WEBSITES COUNT"),
                "screenshots": extract_count("SCREENSHOTS COUNT"),
                "alerts": extract_count("ALERTS COUNT")
            }

        except Exception as e:
            print(f"[ERROR] Failed to read PDF: {e}")
            return {"keystrokes": 0, "websites": 0, "screenshots": 0, "alerts": 0}

    def refresh(self):
        #refresh table used after logout/login
        for row in self.table.get_children():
            self.table.delete(row)
        self.load_sessions()

    def send_selected_reports(self):
        #Zip session and send to SendReportPage
        selected = self.table.focus()
        if not selected:
            messagebox.showerror("No Selection", "Please select a session.")
            return

        session_name = selected  #Treeview row ID is the actual folder name
        session_path = os.path.join(self.logs_root, session_name)

        #Create ZIP files
        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for pc_folder in os.listdir(session_path):
                pc_path = os.path.join(session_path, pc_folder)
                if not os.path.isdir(pc_path):
                    continue

                pdf_path = os.path.join(pc_path, "session_summary.pdf")
                if os.path.exists(pdf_path):
                    arcname = os.path.join(session_name, pc_folder, "session_summary.pdf")
                    zipf.write(pdf_path, arcname)

                screenshots_dir = os.path.join(pc_path, "screenshots")
                if os.path.exists(screenshots_dir):
                    for file in os.listdir(screenshots_dir):
                        file_path = os.path.join(screenshots_dir, file)
                        arcname = os.path.join(session_name, pc_folder, "screenshots", file)
                        zipf.write(file_path, arcname)

        #send to report page
        from proctor_send_report_page import SendReportPage
        self.master.master.pages["SendReportPage"].preload_file(zip_path)
        self.master.master.show_send_page()

    def download_selected_sessions(self):
        #download a ZIP copy of the selected report files
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a session.")
            return

        session = selected
        session_path = os.path.join(self.logs_root, session)

        zip_filename = f"{session}.zip"
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=zip_filename)

        if not zip_path:
            return

        #build ZIP
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for pc_folder in os.listdir(session_path):
                pc_path = os.path.join(session_path, pc_folder)
                if not os.path.isdir(pc_path):
                    continue

                pdf_path = os.path.join(pc_path, "session_summary.pdf")
                if os.path.exists(pdf_path):
                    arcname = os.path.join(pc_folder, "session_summary.pdf")
                    zipf.write(pdf_path, arcname)

                screenshots_dir = os.path.join(pc_path, "screenshots")
                if os.path.exists(screenshots_dir):
                    for file in os.listdir(screenshots_dir):
                        file_path = os.path.join(screenshots_dir, file)
                        arcname = os.path.join(pc_folder, "screenshots", file)
                        zipf.write(file_path, arcname)

        messagebox.showinfo("Download Complete", f"Saved to: {zip_path}")
