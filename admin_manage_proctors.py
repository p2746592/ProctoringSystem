#admin add/delete/update proctors
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ProctorManagementPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.selected_proctors = set() #track selected rows using tags instead of Treeview selection

        #title
        tk.Label(self, text="Proctor Management", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

        #Treeview display proctor records
        columns = ("ID", "Name", "Email")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=8, selectmode="none")
        self.table.pack(side="left", fill="both", expand=True, padx=10)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=180)

        self.table.bind("<Button-1>", self.toggle_selection)

        #button
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(side="left", fill="y", padx=10)

        ttk.Button(button_frame, text="Add Proctors", command=self.add_proctor_popup).pack(pady=5)
        ttk.Button(button_frame, text="Remove Proctors", command=self.remove_selected).pack(pady=5)
        ttk.Button(button_frame, text="Update Proctors", command=self.update_selected_popup).pack(pady=5)

        self.load_proctors()

    def toggle_selection(self, event):
        item = self.table.identify_row(event.y)
        if not item:
            return
        if item in self.selected_proctors:
            self.selected_proctors.remove(item)
            self.table.item(item, tags=())
        else:
            self.selected_proctors.add(item)
            self.table.item(item, tags=("selected",))
        self.style_selected()

    def style_selected(self):
        self.table.tag_configure("selected", background="#d9f1ff")

    def load_proctors(self):
        #load proctor records from the database
        self.table.delete(*self.table.get_children())
        self.selected_proctors.clear()
        conn = sqlite3.connect("monitoring.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM proctors")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        conn.close()

    def add_proctor_popup(self):
        #popup add proctor
        self._proctor_form_popup(title="Add Proctor", on_submit=self.insert_proctor)

    def update_selected_popup(self):
        #update form proctor
        if not self.selected_proctors:
            messagebox.showwarning("None Selected", "Select a proctor to update")
            return
        if len(self.selected_proctors) > 1:
            messagebox.showwarning("Multiple Selected", "Only one proctor can be updated at a time.")
            return
        item = next(iter(self.selected_proctors))
        values = self.table.item(item)["values"]
        self._proctor_form_popup(title="Update Proctor", data=values, on_submit=self.update_proctor)

    def _proctor_form_popup(self, title, data=None, on_submit=None):
        #popup update or add
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("500x300")

        #entry
        tk.Label(popup, text="Proctor ID (number only)").pack(pady=5)
        id_entry = ttk.Entry(popup)
        id_entry.pack()

        tk.Label(popup, text="Full Name").pack(pady=5)
        name_entry = ttk.Entry(popup)
        name_entry.pack()

        tk.Label(popup, text="Email").pack(pady=5)
        email_entry = ttk.Entry(popup)
        email_entry.pack()

        tk.Label(popup, text="Password").pack(pady=5)
        password_entry = ttk.Entry(popup, show="*")
        password_entry.pack()

        #fill existing data (update)
        if data:
            id_entry.insert(0, data[0])
            id_entry.config(state="disabled")  #Not allow changing ID
            name_entry.insert(0, data[1])
            email_entry.insert(0, data[2])

        def submit():
            proctor_id = id_entry.get().strip()
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if not proctor_id.isdigit():
                messagebox.showerror("Invalid ID", "Proctor ID must be numeric.")
                return
            if not all([proctor_id, name, email, password]):
                messagebox.showerror("Missing Info", "Please fill all fields.")
                return

            on_submit(proctor_id, name, email, password)
            popup.destroy()

        ttk.Button(popup, text="Save", command=submit).pack(pady=10)

    def insert_proctor(self, pid, name, email, password):
        #insert new proctor to database
        try:
            conn = sqlite3.connect("monitoring.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO proctors (id, name, email, password) VALUES (?, ?, ?, ?)",
                           (pid, name, email, password))
            conn.commit()
            conn.close()
            self.load_proctors()
            messagebox.showinfo("Success", "Proctor added.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Proctor with this ID already exists.")

    def update_proctor(self, pid, name, email, password):
        #update existing proctor
        conn = sqlite3.connect("monitoring.db")
        cursor = conn.cursor()

        if password:  #if a new password entered
            cursor.execute(
                "UPDATE proctors SET name = ?, email = ?, password = ? WHERE id = ?",
                (name, email, password, pid)
            )
        else:  #xisting password
            cursor.execute(
                "UPDATE proctors SET name = ?, email = ? WHERE id = ?",
                (name, email, pid)
            )

        conn.commit()
        conn.close()
        self.load_proctors()
        messagebox.showinfo("Success", "Proctor updated.")

    def remove_selected(self):
        #delete proctor from table and database
        if not self.selected_proctors:
            messagebox.showwarning("No Selection", "Select at least one proctor.")
            return
        confirm = messagebox.askyesno("Confirm", "Delete selected proctors?")
        if confirm:
            conn = sqlite3.connect("monitoring.db")
            cursor = conn.cursor()
            for item in self.selected_proctors:
                pid = self.table.item(item)["values"][0]
                cursor.execute("DELETE FROM proctors WHERE id = ?", (pid,))
            conn.commit()
            conn.close()
            self.load_proctors()
