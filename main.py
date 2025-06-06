#starting the system

#root = tk.Tk()                         - create main window
#label = tk.Label(root, text="Hi!")     - add label to window
#label.pack()                           - display label
#root.mainloop()                        - keep window open

import tkinter as tk
from login_page import LoginPage                    #import login screen UI
from database import init_db                        #database table exist
from role_launcher import launch_app                #launch Admin & Proctor dashboard
from encryption import generate_key_if_missing      #create encryption key

init_db()                   #create database
generate_key_if_missing()   #create key for encryption

#start login window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Proctoring System Login")
    root.geometry("500x400") #widthxheight

    #login page
    login = LoginPage(root, on_login_success=lambda role, user_id: launch_app(role, user_id, root))
    login.pack(fill="both", expand=True)
    root.mainloop() #keep window running