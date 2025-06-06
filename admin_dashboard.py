#dashboard for Admin users

import tkinter as tk
from sidebar_menu import SidebarMenu
from admin_manage_proctors import ProctorManagementPage
from admin_monitor_reports import ReportsMonitoringPage
from admin_send_report import AdminSendReportPage

class AdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        #window setup
        self.title("Admin Dashboard")
        self.geometry("1200x800")
        self.configure(bg="white")

        #sidebar
        menu_items = {
            "Proctor Accounts": self.show_manage_proctors,
            "Monitor Reports": self.show_monitor_reports,
            "Send Report": self.show_send_report,
            "Logout": self.logout
        }
        SidebarMenu(self, callback_dict=menu_items)

        #content area
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="left", fill="both", expand=True)

        #pages
        self.pages = {
            "ManageProctors": ProctorManagementPage(self.container),
            "MonitorReports": ReportsMonitoringPage(self.container),
            "SendReport": AdminSendReportPage(self.container)
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_manage_proctors()  #show first page on load

    def show_manage_proctors(self):
        self.pages["ManageProctors"].tkraise()

    def show_monitor_reports(self):
        self.pages["MonitorReports"].tkraise()

    def show_send_report(self):
        self.pages["SendReport"].tkraise()

    def refresh(self):
        self.load_sessions()

    def logout(self):
        self.destroy()
        #relaunch login screen
        import tkinter as tk
        from login_page import LoginPage
        from role_launcher import launch_app

        root = tk.Tk()
        root.title("Login")
        root.geometry("500x400")

        login_page = LoginPage(root, on_login_success=lambda role, user_id: launch_app(role, user_id, root))
        login_page.pack(fill="both", expand=True)
        root.mainloop()
