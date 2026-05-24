from datetime import datetime
from dotenv import load_dotenv
import logging
import os

from app.sensor_internal import VcgencmdSensor
from app.communication import send_temperature

LOG_FILE = "/home/klaus/PROD/alectryon.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def load_config():
    load_dotenv()  # lädt .env aus dem gleichen Verzeichnis


def main():
    # Dies wird nach dem Starten des Raspberry regelmäßig alle 15 Minuten ausgeführt
    load_config()
    log.info("Programm gestartet")

    try:
        temp = VcgencmdSensor().read_temp_celsius()
        log.info(f"Interne Temperatur: {temp:.1f} °C")
    except Exception:
        log.exception("Fehler beim Lesen der internen Temperatur")
        return

    stunde = datetime.now().hour
    if 6 <= stunde < 23:
        log.info("Innerhalb der Sendezeit – sende Temperatur...")
        try:
            send_temperature(temp)
        except Exception:
            log.exception("Fehler beim Senden der Temperatur")
    else:
        log.info("Außerhalb der Sendezeit (06–23 Uhr) – kein Versand.")


if __name__ == "__main__":
    main()