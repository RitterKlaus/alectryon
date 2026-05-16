import subprocess
import signal
import sys
from app.rtc_modul import schedule_wakeup
from dotenv import load_dotenv
import os

def load_config():
    load_dotenv()  # lädt .env aus dem gleichen Verzeichnis
    ftp_host     = os.getenv("FTP_HOST")
    ftp_user     = os.getenv("FTP_USER")
    ftp_password = os.getenv("FTP_PASSWORD")
    ftp_port     = int(os.getenv("FTP_PORT", 21))  # 21 als Standardwert

def cleanup_and_shutdown():
    # z.B. Datei speichern, GPIO zurücksetzen...
    print("Fahre herunter...")
    subprocess.run(["sudo", "shutdown", "-h", "now"])

# Auf Strg+C oder kill reagieren
signal.signal(signal.SIGTERM, lambda s, f: cleanup_and_shutdown())
signal.signal(signal.SIGINT, lambda s, f: cleanup_and_shutdown())

def main():
    # Dies wird nach dem Starten des Rapsberry regelmäßig ausgeführt
    load_config()
    print("Das Programm wurde gestartet!")
    schedule_wakeup(15)
    print("Alarm wurde gesetzt!")
    print()

if __name__ == "__main__":
    main()