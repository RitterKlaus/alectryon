import ftplib
import os
import shutil
import subprocess
from datetime import datetime

CAMERA_DIR = "camera"

# Absolute Fallback-Pfade für den eingeschränkten PATH im systemd-Service.
# Bookworm nennt das Tool rpicam-still; Bullseye noch libcamera-still.
_CAMERA_CANDIDATES = [
    "rpicam-still",
    "libcamera-still",
    "/usr/bin/rpicam-still",
    "/usr/bin/libcamera-still",
]


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


def _find_camera_binary() -> str:
    for candidate in _CAMERA_CANDIDATES:
        path = shutil.which(candidate) or (candidate if os.path.isfile(candidate) else None)
        if path:
            return path
    raise FileNotFoundError(
        f"Kein Kamera-Binary gefunden. Gesucht: {_CAMERA_CANDIDATES}"
    )


def take_photo() -> str:
    """Nimmt ein Foto auf und speichert es in camera/. Gibt den Dateipfad zurück."""
    os.makedirs(CAMERA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(CAMERA_DIR, f"{timestamp}.jpg")

    if _dev_mode():
        return filename

    binary = _find_camera_binary()
    result = subprocess.run(
        [binary, "--nopreview", "--rotation", "180", "-t", "500", "-o", filename],
        capture_output=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    return filename


def upload_photo(filename: str) -> None:
    """Lädt ein Foto per FTPS auf den konfigurierten FTP-Server hoch."""
    if _dev_mode():
        return

    host     = os.getenv("FTP_HOST")
    user     = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASSWORD")
    port     = int(os.getenv("FTP_PORT", "21"))

    with ftplib.FTP_TLS() as ftp:
        ftp.connect(host, port)
        ftp.login(user, password)
        ftp.prot_p()  # verschlüsselten Datenkanal aktivieren
        with open(filename, "rb") as f:
            ftp.storbinary(f"STOR {os.path.basename(filename)}", f)
