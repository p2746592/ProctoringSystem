#sidebar navigation used in dashboards
import tkinter as tk

class SidebarMenu(tk.Frame):
    def __init__(self, parent, callback_dict):
        super().__init__(parent, bg="#2c3e50", width=150)

        self.pack_propagate(0)  #prevent sidebar from resizing with content
        self.pack(side="left", fill="y")  #pin to the left side

        #add a button for each label
        for label, command in callback_dict.items():
            btn = tk.Button(
                self,
                text=label,
                command=command,
                bg="#2c3e50",
                fg="white",
                font=("Helvetica", 11),
                relief="flat",
                anchor="w",
                padx=10
            )
            btn.pack(fill="x", pady=5)  # Full-width buttons with vertical spacing
