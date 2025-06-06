#proctor start monitoring, configure setting, view reports, and send reports

import tkinter as tk                                    #GUI components
from sidebar_menu import SidebarMenu                    #sidebar menu
from proctor_status_page import ProctorStatusPage       #monitoring status page
from proctor_setup_page import SetupPage                #setup page
from proctor_reports_page import ReportsPage            #report page
from proctor_send_report_page import SendReportPage     #email page
from login_page import LoginPage                        #login page
from role_launcher import launch_app                    #open dashbaord


#main window for proctors
class ProctorDashboard(tk.Tk):
    def __init__(self, proctor_email):
        super().__init__()
        self.proctor_email = proctor_email

        self.title("Proctor Dashboard")                 #window title
        self.geometry("1200x800")                       #window size
        self.configure(bg="white")                      #background colour

        #sidebar
        menu_items = {
            "Status": self.show_status_page,
            "Setup": self.show_setup_page,
            "Reports": self.show_reports_page,
            "Send Report": self.show_send_page,
            "Logout": self.logout
        }

        # create sidebar
        SidebarMenu(self, callback_dict=menu_items)

        #container for all pages
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="left", fill="both", expand=True)

        status_page = ProctorStatusPage(self.container, self.proctor_email)

        self.pages = {
            "StatusPage": status_page,
            "SetupPage": SetupPage(self.container, update_settings_callback=status_page.update_settings),
            "ReportsPage": ReportsPage(self.container, self.proctor_email),
            "SendReportPage": SendReportPage(self.container)
        }

        #place each page in the same position
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        # show status page first
        self.show_status_page()

    #status page
    def show_status_page(self):
        self.pages["StatusPage"].tkraise()

    #setup page
    def show_setup_page(self):
        self.pages["SetupPage"].tkraise()

    #report page
    def show_reports_page(self):
        self.pages["ReportsPage"].refresh() #load latest data
        self.pages["ReportsPage"].tkraise()

    #email page
    def show_send_page(self):
        self.pages["SendReportPage"].tkraise()

    #logout and return login window
    def logout(self):

        # Cancel live update if StatusPage running
        status_page = self.pages.get("StatusPage")
        if hasattr(status_page, "after_id"):
            status_page.after_cancel(status_page.after_id)

        self.destroy()

        #relaunch login screen
        root = tk.Tk()
        root.title("Login")
        root.geometry("500x400")

        login_page = LoginPage(root, on_login_success=lambda role, user_id: launch_app(role, user_id, root))
        login_page.pack(fill="both", expand=True)
        root.mainloop()



