# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**alectryon** ist eine Python-Anwendung für einen solar-betriebenen Raspberry Pi Zero, der energiesparend Sensordaten misst und (per FTP) überträgt. Der Pi fährt nach jeder Messung wieder herunter, um Strom zu sparen.

## Deployment / Ausführung

Die Anwendung läuft **nicht lokal entwickelbar** – sie braucht Raspberry-Pi-Hardware (I2C, 1-Wire, `vcgencmd`). Tests auf dem Pi:

```bash
# Manuell starten (als User klaus im Prod-Verzeichnis)
cd /home/klaus/PROD/alectryon && python3 app/main.py

# Timer-Status und Logs
systemctl list-timers measure.timer
journalctl -u measure.service -n 50

# Anwendungs-Log
tail -f /home/klaus/PROD/alectryon.log
```

## Betriebszyklus (Architektur)

```
Pi bootet  (alle 15 Minuten per measure.timer)
  → measure.service startet manage.sh
    → git fetch/pull (Auto-Update)
    → python3 app/main.py
      → interne CPU-Temperatur lesen
      → wenn 06–23 Uhr: Temperatur per API senden
      → (weitere Sensoren folgen)
```

**Hinweis:** Der RTC-Wakeup-Alarm (SQW-Pin → GPIO3/SCL) ist **nicht realisiert** – der SQW-Pin kollidiert mit dem I2C-Bus (Solar-HAT über Pogo-Pins). Das Timing übernimmt `measure.timer` (systemd, alle 15 Minuten).

## Konfiguration

`app/.env` (nach `app/.env.example` anlegen):
```
FTP_HOST=ftp.example.com
FTP_USER=meinuser
FTP_PASSWORD=geheimespasswort
FTP_PORT=21

API_URL=https://localhost:8000/api/temperatur
API_KEY=geheimer-schluessel-hier
```

## Module

| Datei | Zweck |
|-------|-------|
| `app/main.py` | Einstiegspunkt; koordiniert Messen, Zeitprüfung, Senden; schreibt Log nach `/home/klaus/PROD/alectryon.log` |
| `app/sensor_internal.py` | Interne CPU-Temperatur und Spannung via `vcgencmd` (`VcgencmdSensor`) |
| `app/sensor_temperatur.py` | DS18B20-Temperatursensoren über 1-Wire (`/sys/bus/w1/devices/28-*`) |
| `app/sensor_rtc.py` | DS3231 RTC (I2C, Adresse 0x68) – in Entwicklung |
| `app/sensor_usv.py` | USV/Solar-HAT-Sensor – in Entwicklung |
| `app/communication.py` | HTTP-POST der Messwerte an die REST-API (`send_temperature`) |
| `scripts/manage.sh` | Wird vom Service aufgerufen: git-Update + Programm starten |
| `scripts/install.sh` | Einmalige Installation auf dem Pi (klont Repo, richtet measure.timer ein) |

## Ablauf in main.py

1. `.env` laden (`load_dotenv`)
2. Interne Temperatur lesen (`VcgencmdSensor().read_temp_celsius()`)
3. Aktuelle Stunde prüfen: nur zwischen **06:00 und 22:59 Uhr** wird gesendet
4. `send_temperature(temp)` → HTTP-POST an `API_URL` mit Bearer-Token
5. Fehler werden mit `log.exception` inkl. Traceback ins Log geschrieben

## Abhängigkeiten

Python-Pakete (müssen auf dem Pi installiert sein):
- `smbus2` – I2C-Kommunikation
- `python-dotenv` – `.env`-Datei laden
- `requests` – HTTP-Versand in `communication.py`

Systemprogramme:
- `vcgencmd` – Raspberry-Pi-eigenes Tool (Teil von `libraspberrypi-bin`)
- `modprobe` – für RTC-Treiber-Reload bei direktem I2C-Zugriff

## Wichtige Hinweise zum DS3231

- I2C-Adresse: **0x68**
- Beim direkten smbus2-Zugriff muss der Kernel-Treiber (`rtc_ds1307`) vorher per `modprobe -r` entladen werden, sonst schlägt der Bus-Zugriff fehl
- Der DS3231 speichert die Zeit in **UTC** – bei Alarm-Zeiten muss von lokaler Zeit umgerechnet werden
- `/boot/firmware/config.txt` muss `dtoverlay=i2c-rtc,ds3231` enthalten
