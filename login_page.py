#login UI and verify

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class LoginPage(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg="#f9f9f9")
        self.on_login_success = on_login_success #callback to launch dashboard

        #title
        tk.Label(self, text="Proctoring System", font=("Helvetica", 22, "bold"), bg="#f9f9f9").pack(pady=30)

        #login container
        form = tk.Frame(self, bg="#f9f9f9")
        form.pack(pady=10)

        #username field
        tk.Label(form, text="ID / Email", font=("Helvetica", 13), bg="#f9f9f9").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = ttk.Entry(form, width=35)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        #password field
        tk.Label(form, text="Password", font=("Helvetica", 13), bg="#f9f9f9").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = ttk.Entry(form, show="*", width=35)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        #login button
        ttk.Button(self, text="Login", command=self.validate_login).pack(pady=20, ipadx=10)

    #login button press
    def validate_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        #admin account
        if username == "admin" and password == "admin":
            self.on_login_success("Admin", "admin")

        #proctor account (check database)
        elif self.validate_proctor(username, password):
            self.on_login_success("Proctor", username)

        else: messagebox.showerror("Login Failed", "Invalid credentials.")

    def validate_proctor(self, username, password): #check if proctor exists in database. return true if password match
        import sqlite3
        conn = sqlite3.connect("monitoring.db")
        cursor = conn.cursor()

        #search ID or Email
        cursor.execute("SELECT * FROM proctors WHERE id = ? OR email = ?", (username, username))
        row = cursor.fetchone()
        conn.close()

        if row:
            db_password = row[3]  #4th column is password
            return db_password == password
        return False



