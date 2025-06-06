from flask import Flask, request, jsonify
from collections import defaultdict
import os
import time

app = Flask(__name__)

#store session state: whether a session is active and name per proctor
session_states = {
    "2": {"active": False, "session_name": ""}
}

#track the last heartbeat timestamp from each student PC
#format: heartbeat_map[proctor_id][pc_id] = last_seen_timestamp
heartbeat_map = defaultdict(dict)


@app.route("/status/<proctor_id>")
def check_status(proctor_id):
    #used by student clients to check if the session should begin
    state = session_states.get(proctor_id, {"active": False})
    return "start" if state["active"] else "wait"


@app.route("/upload", methods=["POST"])
def upload_log():
    #receive and store uploaded log files from student
    proctor_id = request.form.get("proctor_id")
    session_name = request.form.get("session_name")
    file = request.files.get("file")

    if not all([proctor_id, session_name, file]):
        return "Missing data", 400

    save_path = os.path.join("received_logs", proctor_id, session_name)
    os.makedirs(save_path, exist_ok=True)

    file_path = os.path.join(save_path, file.filename)
    file.save(file_path)

    print(f"[UPLOAD] {file.filename} saved to {file_path}")
    return "OK", 200


@app.route("/heartbeat", methods=["POST"])
def receive_heartbeat():
    #heartbeat pings from student
    data = request.get_json()
    proctor_id = data.get("proctor_id")
    pc_id = data.get("pc_id")
    now = time.time()

    if proctor_id and pc_id:
        heartbeat_map[proctor_id][pc_id] = now
        return "OK", 200

    return "Missing data", 400


@app.route("/status_table/<proctor_id>")
def status_table(proctor_id):
    now = time.time()
    timeout = 15
    table = []

    for pc_id, last_seen in heartbeat_map.get(proctor_id, {}).items():
        status = "CONNECTED" if now - last_seen <= timeout else "DISCONNECTED"
        table.append({"pc_id": pc_id, "status": status})

    return jsonify(table)


@app.route("/toggle/<proctor_id>", methods=["POST"])
def toggle_session(proctor_id):
    #Proctor start or stop a session
    start = request.json.get("start", False)
    session_name = request.json.get("session_name", "")

    session_states[proctor_id] = {
        "active": start,
        "session_name": session_name
    }

    return jsonify(session_states[proctor_id])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
