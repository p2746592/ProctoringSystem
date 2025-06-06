#SQLite tables with optional session tracking

import sqlite3

def init_db():
    #proctors (login)
    #keystrokes (with session tracking)
    #emails (log of sent reports)

    conn = sqlite3.connect("monitoring.db")
    cursor = conn.cursor()

    #login credentials
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proctors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    #keystroke session info
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keystrokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')

    #email history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            timestamp TEXT,
            attachment_path TEXT
        )
    ''')

    conn.commit()
    conn.close()
