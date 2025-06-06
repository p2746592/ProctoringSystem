import os, shutil, sqlite3, tempfile, zipfile
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from cryptography.fernet import Fernet
from tkinter import filedialog


class ReportsMonitoringPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        #title
        tk.Label(self, text="Reports Monitoring", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

        #table with report
        columns = ("proctor_id", "proctor_name", "session_name", "date", "time")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=20)
        self.table.pack(fill="both", expand=True, padx=20)

        #button
        ttk.Button(self, text="Send Report", command=self.send_selected_report).pack(pady=5)
        ttk.Button(self, text="Download & Decrypt Logs", command=self.download_and_decrypt_logs).pack(pady=5)

        #table column setup
        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").capitalize())
            self.table.column(col, anchor="center", width=160)

        self.load_logs()

    def load_logs(self):
        #load all session
        proctor_map = self.fetch_proctor_names()

        base_path = os.path.join(os.path.expanduser("~"), "OneDrive - De Montfort University", "shared_report")
        if not os.path.exists(base_path):
            return

        for proctor_id in os.listdir(base_path):
            proctor_folder = os.path.join(base_path, proctor_id)
            if not os.path.isdir(proctor_folder):
                continue

            for session in os.listdir(proctor_folder):
                if not session.startswith("session_"):
                    continue

                session_path = os.path.join(proctor_folder, session)
                session_name = session

                #extract date & time from folder name
                parts = session_name.split("_")
                try:
                    date_part = "_".join(parts[-2:])
                    session_base = session  # Keep full folder name
                    dt = datetime.strptime(date_part, "%Y-%m-%d_%H-%M-%S")
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    session_base = session_name
                    date_str, time_str = "Unknown", "Unknown"

                #insert row in the table
                self.table.insert("", "end", values=(
                    proctor_id,
                    proctor_map.get(proctor_id, "Unknown"),
                    session_name,  # ✅ full session folder name
                    date_str,
                    time_str
                ))

    def fetch_proctor_names(self):
        conn = sqlite3.connect("monitoring.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM proctors")
        data = {str(row[0]): row[1] for row in cursor.fetchall()}
        conn.close()
        return data

    def send_selected_report(self):
        #compress and send report email
        selected = self.table.focus()
        if not selected:
            messagebox.showerror("No Selection", "Please select a session.")
            return

        values = self.table.item(selected)["values"]
        proctor_id, _, session_name, _, _ = values

        #locate session folder
        session_path = os.path.join(
            os.path.expanduser("~"),
            "OneDrive - De Montfort University",
            "shared_report",
            str(proctor_id),
            session_name
        )

        if not os.path.exists(session_path):
            messagebox.showerror("Missing Folder", "Session folder not found.")
            return

        #zip session folder
        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(session_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, session_path)
                    zipf.write(full_path, arcname=os.path.join(session_name, arcname))

        #send to SendReportPage
        self.master.master.pages["SendReport"].preload_file(zip_path)
        self.master.master.show_send_report()

    def download_and_decrypt_logs(self):
        #download and decrypt all encryption .txt
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a session.")
            return

        values = self.table.item(selected)["values"]
        proctor_id, _, session_name, _, _ = values

        #locate session folder
        session_folder = os.path.join(
            os.path.expanduser("~"),
            "OneDrive - De Montfort University",
            "shared_report",
            str(proctor_id),
            session_name
        )

        if not os.path.exists(session_folder):
            messagebox.showerror("Not Found", f"Session folder not found:\n{session_folder}")
            return

        #choose where to save
        save_to = filedialog.askdirectory(title="Save decrypted session to:")
        if not save_to:
            return

        #copy entire session folder
        destination = os.path.join(save_to, f"{session_name}_decrypted")
        shutil.copytree(session_folder, destination, dirs_exist_ok=True)

        #load encryption key from secret.key
        try:
            with open("secret.key", "rb") as f:
                key = Fernet(f.read())
        except:
            messagebox.showerror("Missing Key", "secret.key not found.")
            return

        #decctypt all encryption files
        decrypted_count = 0

        for root, _, files in os.walk(destination):
            for file in files:
                if file.endswith(".txt"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "rb") as enc:
                            content = enc.read()
                        decrypted = key.decrypt(content)

                        # Overwrite the original file with decrypted content
                        with open(path, "wb") as out:
                            out.write(decrypted)

                        decrypted_count += 1
                    except Exception as e:
                        print(f"[SKIPPED] {file} — not encrypted or failed to decrypt.")

        #show results message
        if decrypted_count == 0:
            messagebox.showwarning("No Decryption",
                                   "No files were decrypted. They may not be encrypted or were skipped.")
        else:
            messagebox.showinfo("Done", f"{decrypted_count} files decrypted.\nSaved to:\n{destination}")


