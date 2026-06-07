from datetime import datetime
from dotenv import load_dotenv
import logging
import os

from app.camera import take_photo, upload_photo
from app.sensor_internal import VcgencmdSensor
from app.sensor_usv import UsvSensor
from app.communication import send_data

LOG_FILE = "alectryon.log"

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

    try:
        usv = UsvSensor().read()
        log.info(f"USV – Spannung: {usv['spannung_v']} V | "
                 f"Strom: {usv['strom_ma']} mA | "
                 f"Leistung: {usv['leistung_w']} W | "
                 f"Ladestand: {usv['ladestand_pz']} %")
    except Exception:
        log.exception("Fehler beim Lesen der USV-Daten")
        usv = None

    stunde = datetime.now().hour
    if 6 <= stunde < 23:
        log.info("Innerhalb der Sendezeit – sende Daten...")
        try:
            send_data(temp, usv)
        except Exception:
            log.exception("Fehler beim Senden der Daten")

        if usv is not None and usv["ladestand_pz"] > 50:
            try:
                filename = take_photo()
                log.info(f"Foto gespeichert: {filename}")
                upload_photo(filename)
                log.info(f"Foto hochgeladen: {os.path.basename(filename)}")
            except Exception:
                log.exception("Fehler bei Foto oder Upload")
    else:
        log.info("Außerhalb der Sendezeit (06–23 Uhr) – kein Versand.")


if __name__ == "__main__":
    main()