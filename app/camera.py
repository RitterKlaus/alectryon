import os
import subprocess
from datetime import datetime

CAMERA_DIR = "camera"


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


def take_photo() -> str:
    """Nimmt ein Foto auf und speichert es in camera/. Gibt den Dateipfad zurück."""
    os.makedirs(CAMERA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(CAMERA_DIR, f"{timestamp}.jpg")

    if _dev_mode():
        return filename

    result = subprocess.run(
        ["libcamera-still", "--nopreview", "-t", "500", "-o", filename],
        capture_output=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    return filename
