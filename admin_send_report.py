import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import sqlite3
from datetime import datetime

class AdminSendReportPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.selected_files = []

        #itle
        tk.Label(self, text="📧 Admin Send Report", font=("Helvetica", 16, "bold"), bg="white").pack(pady=15)

        #recipient Email
        self.recipient_entry = self.labeled_entry("Recipient Email")

        #subject
        self.subject_entry = self.labeled_entry("Subject")

        #message Body
        tk.Label(self, text="Message", bg="white").pack()
        self.body_text = tk.Text(self, width=60, height=10, wrap="word", font=("Helvetica", 10))
        self.body_text.pack(pady=5)

        #buttons
        ttk.Button(self, text="Attach Files", command=self.attach_files).pack(pady=10)
        ttk.Button(self, text="Send Email", command=self.send_email).pack(pady=10)

    def labeled_entry(self, label_text):
        tk.Label(self, text=label_text, bg="white").pack()
        entry = ttk.Entry(self, width=50)
        entry.pack(pady=5)
        return entry

    def attach_files(self):
        files = filedialog.askopenfilenames(title="Select Files to Attach")
        if files:
            self.selected_files = list(set(self.selected_files + list(files)))
            messagebox.showinfo("Files Attached", f"{len(self.selected_files)} file(s) selected.")

    def send_email(self):
        recipient = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", "end").strip()

        if not subject or not body:
            messagebox.showerror("Missing Info", "Please fill in both the subject and message.")
            return

        try:
            msg = MIMEMultipart()
            sender_email = "fyprojectkey@gmail.com"
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            for file in self.selected_files:
                with open(file, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file)}")
                    msg.attach(part)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, "enka rqfz ghzy sjhy")  # app password
            server.sendmail(sender_email, recipient, msg.as_string())
            server.quit()

            attachment_path = self.selected_files[0] if self.selected_files else None
            self.log_email(sender_email, recipient, subject, body, attachment_path)

            messagebox.showinfo("Success", "Email sent successfully!")

            #clear form after sending
            self.recipient_entry.config(state="normal")
            self.recipient_entry.delete(0, tk.END)
            self.subject_entry.delete(0, tk.END)
            self.body_text.delete("1.0", tk.END)
            self.selected_files = []

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email:\n{e}")

    def preload_file(self, file_path):
        if os.path.exists(file_path):
            self.selected_files = list(set(self.selected_files + [file_path]))
            messagebox.showinfo("File Preloaded", "Report ZIP file is ready to send.")

    def log_email(self, sender, recipient, subject, body, attachment_path):
        conn = sqlite3.connect("monitoring.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                timestamp TEXT,
                attachment_path TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO emails (sender, recipient, subject, body, timestamp, attachment_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sender, recipient, subject, body, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), attachment_path))
        conn.commit()
        conn.close()