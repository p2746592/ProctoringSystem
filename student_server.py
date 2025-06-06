import os
import time
import socket
import threading
import requests
from datetime import datetime

#configuration
SERVER_URL = "http://172.16.2.204:5000"   #Proctor IP
PROCTOR_ID = "2"
PC_ID = socket.gethostname()  #computer name
SESSION_NAME = f"session_{PC_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

#store logs
TEMP_DIR = os.path.join(os.environ["TEMP"], SESSION_NAME)
os.makedirs(TEMP_DIR, exist_ok=True)


def wait_for_start():
    print(f"[{PC_ID}] Waiting...")
    while True:
        try:
            r = requests.get(f"{SERVER_URL}/status/{PROCTOR_ID}")
            if r.text.strip().lower() == "start":
                print("Session start")
                break
        except:
            pass
        time.sleep(5)

def upload_logs():
   #generated log files
    for root, _, files in os.walk(TEMP_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, TEMP_DIR)

            with open(full_path, "rb") as f:
                files_data = {"file": (relative_path, f)}
                data = {
                    "proctor_id": PROCTOR_ID,
                    "session_name": SESSION_NAME
                }
                try:
                    r = requests.post(f"{SERVER_URL}/upload", data=data, files=files_data)
                    print(f"[UPLOAD] {relative_path} → {r.status_code}")
                except Exception as e:
                    print(f"[ERROR] Failed to upload {file}: {e}")


def send_heartbeat():
    #PC is connected
    while True:
        try:
            r = requests.post(f"{SERVER_URL}/heartbeat", json={
                "proctor_id": PROCTOR_ID,
                "session_name": SESSION_NAME,
                "pc_id": PC_ID
            })
        except:
            pass
        time.sleep(5)


if __name__ == "__main__":
    wait_for_start()
    threading.Thread(target=send_heartbeat, daemon=True).start()
    upload_logs()
    print(f"[{PC_ID}]Monitoring complete.")
