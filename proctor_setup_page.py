#configuring monitoring settings - intervals, keywords, websites
import tkinter as tk
from tkinter import ttk, messagebox

class SetupPage(tk.Frame):
    def __init__(self, parent, update_settings_callback=None):
        super().__init__(parent, bg="white")  # Set background color

        self.update_settings_callback = update_settings_callback  #callback to update settings in status page

        #page title
        tk.Label(self, text="Setup Page", font=("Helvetica", 18, "bold"), bg="white").pack(pady=20)

        #form container
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        #interval input
        self._create_input(form_frame, "Screenshot Interval (seconds):", "3", "screenshot_interval_entry")

        #flagged keywords input
        self._create_input(form_frame, "Flagged Keywords (comma separated):", "password, cheat, answer", "flagged_keywords_entry")

        #flagged websites input
        self._create_input(form_frame, "Flagged Websites (comma separated):", "chatgpt, google", "flagged_websites_entry")

        #apply changes button
        ttk.Button(self, text="Apply Changes", command=self.apply_settings).pack(pady=20)

    def _create_input(self, parent, label_text, default_value, attr_name):
        #create a labeled input field and assign it as an attribute
        tk.Label(parent, text=label_text, font=("Helvetica", 12), bg="white").pack(pady=5, anchor="w")
        entry = ttk.Entry(parent, width=60)
        entry.insert(0, default_value)
        entry.pack(pady=5)
        setattr(self, attr_name, entry)  #save input as attribute

    def apply_settings(self):
        try:
            #convert screenshot interval to number
            interval = int(self.screenshot_interval_entry.get())

            #comma separated values
            keywords = self.flagged_keywords_entry.get().split(',')
            websites = self.flagged_websites_entry.get().split(',')

            #send to status page
            if self.update_settings_callback:
                self.update_settings_callback(interval, keywords, websites)

            messagebox.showinfo("Success", "Settings applied successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the interval!")
