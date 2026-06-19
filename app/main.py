from datetime import datetime
from dotenv import load_dotenv
import logging
import os
import subprocess

from app.camera import take_photo, upload_photo
from app.sensor_internal import VcgencmdSensor
from app.sensor_sunlight import SunlightSensor
from app.sensor_temperatur import W1Sensoren
from app.sensor_usv import UsvSensor
from app.communication import send_data, send_nachricht

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

    try:
        w1 = W1Sensoren().read()
        log.info(f"1-Wire – Innen: {w1.get('temp_innen')} °C | "
                 f"Außen: {w1.get('temp_aussen')} °C")
    except Exception:
        log.exception("Fehler beim Lesen der 1-Wire-Sensoren")
        w1 = None

    stunde = datetime.now().hour
    if 6 <= stunde < 23:
        log.info("Innerhalb der Sendezeit – sende Daten...")
        try:
            send_data(temp, usv, w1)
        except Exception:
            log.exception("Fehler beim Senden der Daten")

        if usv is not None and usv["ladestand_pz"] > 30:
            if SunlightSensor().is_daytime():
                try:
                    filename = take_photo()
                    log.info(f"Foto gespeichert: {filename}")
                    upload_photo(filename)
                    log.info(f"Foto hochgeladen: {os.path.basename(filename)}")
                    send_nachricht("Neues Foto verfügbar!")
                except Exception:
                    log.exception("Fehler bei Foto oder Upload")
            else:
                log.info("Kein Foto – außerhalb der Tageslichtstunden.")
    else:
        log.info("Außerhalb der Sendezeit (06–23 Uhr) – kein Versand.")

    if usv is not None and usv["ladestand_pz"] < 13:
        log.warning(f"Ladestand kritisch ({usv['ladestand_pz']} %) – fahre herunter.")
        try:
            send_nachricht(f"Ladestand kritisch: {usv['ladestand_pz']} % – Raspberry fährt herunter.")
        except Exception:
            log.exception("Fehler beim Senden der Nachricht")
        subprocess.run(["sudo", "shutdown", "-h", "now"])

    if temp > 75:
        log.warning(f"CPU-Temperatur kritisch ({temp:.1f} °C) – fahre herunter.")
        try:
            send_nachricht(f"CPU-Temperatur kritisch: {temp:.1f} °C – Raspberry fährt herunter.")
        except Exception:
            log.exception("Fehler beim Senden der Nachricht")
        subprocess.run(["sudo", "shutdown", "-h", "now"])


if __name__ == "__main__":
    main()