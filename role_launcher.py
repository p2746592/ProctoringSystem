#open the correct dashboard based on the user roles

def launch_app(role, user_id=None, previous_window=None):

    #close window if exist
    if previous_window:
        previous_window.destroy()

    #proctor dashboard
    if role == "Proctor":
        from proctor_dashboard import ProctorDashboard
        proctor_email = user_id #user id is the email used for login
        app = ProctorDashboard(proctor_email=proctor_email)
        app.mainloop()

    #admin dashboard
    elif role == "Admin":
        from admin_dashboard import AdminDashboard
        app = AdminDashboard()
        app.mainloop()




