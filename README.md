SYSTEM RUN INSTRUCTIONS

Project Title: Enhanced Academic Integrity: Proctoring System for Preventing Cheating in Online Examinations


1. WHAT YOU NEED TO INSTALL

- Python 3.10 or 3.11
- Required Python Packages: pip install -r requirements.txt

2. SYSTEM FILE STRUCTURE
Project Root Folder Includes:

- main.py
- proctor_server.py
- student_server.py
- *.py files (keystroke.py, screenshots.py, etc.)
- secret.key
- requirements.txt
- shared_report/
- monitoring.db


3. HOW TO RUN THE SYSTEM

Step 1: Start the Proctor Server

Step 2: Launch the Proctor Dashboard

Run this: >>> python main.py
- Login as "ADMIN" | ID: admin Password: admin
- create Proctor
- logout
- Login as "PROCTOR" 
- Go to "Status" page
- Click "Start Monitoring" to begin logging
