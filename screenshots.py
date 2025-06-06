#captures screenshots
import os
import time
import threading
import datetime
from PIL import ImageGrab  #Pillow library for screen capture

class ScreenshotCapture:
    def __init__(self, screenshot_dir="screenshots", interval=5, on_screenshot_taken=None):
        self.screenshot_dir = screenshot_dir      #folder to save images
        self.interval = interval                  #time gap between captures
        self.on_screenshot_taken = on_screenshot_taken
        self.running = False                      #monitoring state
        self.logfile = os.path.join(self.screenshot_dir, "screenshots_log.txt")
        self.screenshot_count = 0                 #internal counter

        # Create the screenshot directory if missing
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def start(self):
        #Start screenshot in a separate thread
        self.running = True
        thread = threading.Thread(target=self.schedule_screenshot, daemon=True)
        thread.start()
        print("Screenshot capture started.")

    def stop(self):
        #stop screenshots
        self.running = False
        print("Screenshot capture stopped.")

    def capture_screenshot(self):
        #take screenshot and save it to file with a timestamp
        self.screenshot_count += 1
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_#{self.screenshot_count}_{timestamp}.png"
        screenshot_path = os.path.join(self.screenshot_dir, filename)

        try:
            #capture and save image
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)

            #log the path with timestamp
            with open(self.logfile, "a") as f:
                f.write(f"[{timestamp}] {screenshot_path}\n")

            if self.on_screenshot_taken:
                self.on_screenshot_taken(screenshot_path)

            print(f"[LOG] Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")

    def schedule_screenshot(self):
        #continuously take screenshots every interval
        while self.running:
            start = time.time()
            self.capture_screenshot()
            while self.running and time.time() - start < self.interval:
                time.sleep(0.1)

    def set_logfile(self, path):
        #allow other classes to change the log path
        self.logfile = path
