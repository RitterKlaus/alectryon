# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**alectryon** ist eine Python-Anwendung für einen solar-betriebenen Raspberry Pi Zero, der energiesparend Sensordaten misst und (per FTP) überträgt. Der Pi fährt nach jeder Messung wieder herunter, um Strom zu sparen.

## Deployment / Ausführung

Die Anwendung läuft **nicht lokal entwickelbar** – sie braucht Raspberry-Pi-Hardware (I2C, 1-Wire, `vcgencmd`). Tests auf dem Pi:

```bash
# Service-Status prüfen
sudo systemctl status alectryon

# Logs ansehen
journalctl -u alectryon -n 50

# Manuell starten (als User klaus im Prod-Verzeichnis)
cd /home/klaus/PROD/alectryon && python3 app/main.py
```

Für den alternativen Timer-Ansatz (measure.service/timer):
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now measure.timer
systemctl list-timers measure.timer
journalctl -u measure.service -n 50
```

## Betriebszyklus (Architektur)

```
Pi bootet
  → alectryon.service startet manage.sh
    → git fetch/pull (Auto-Update)
    → python3 app/main.py
      → RTC-Alarm setzen (in N Minuten)
      → Sensordaten messen
      → Daten per FTP hochladen
      → sudo shutdown -h now
  → Pi schläft bis RTC-Alarm
  → Pi bootet erneut (Zyklus wiederholt sich)
```

**Wichtig:** Der RTC-Wakeup-Alarm (SQW-Pin → GPIO3/SCL) ist aktuell **nicht realisiert**, weil der SQW-Pin mit dem I2C-Bus kollidiert (Solar-HAT über Pogo-Pins). Stattdessen wird ein `measure.timer` (systemd) als Timing-Mechanismus evaluiert.

## Konfiguration

`app/.env` (nach `app/.env.example` anlegen):
```
FTP_HOST=ftp.example.com
FTP_USER=meinuser
FTP_PASSWORD=geheimespasswort
FTP_PORT=21
```

## Module

| Datei | Zweck |
|-------|-------|
| `app/main.py` | Einstiegspunkt; lädt Config, setzt RTC-Alarm, koordiniert Ablauf |
| `app/rtc_modul.py` | DS3231 RTC via I2C (smbus2): Alarm 1 setzen (Adresse 0x68) |
| `app/rtc_wakeup.py` | Experimentell: RTC-Alarm mit UTC-Umrechnung + Treiber-Reload |
| `app/rtc_wakeup_working_utc.py` | Funktionierender Stand: Treiber entladen → direkt per smbus2 schreiben → Treiber neu laden |
| `app/temperatur_modul.py` | DS18B20-Sensoren über 1-Wire (`/sys/bus/w1/devices/28-*`) |
| `app/vcgencmd.py` | CPU-Temperatur und Spannung via `vcgencmd`-CLI-Tool |
| `scripts/manage.sh` | Wird vom Service aufgerufen: git-Update + Programm starten |
| `scripts/install.sh` | Einmalige Installation auf dem Pi (klont Repo, richtet Service ein) |

## Abhängigkeiten

Python-Pakete (müssen auf dem Pi installiert sein):
- `smbus2` – I2C-Kommunikation mit dem DS3231
- `python-dotenv` – `.env`-Datei laden

Systemprogramme:
- `vcgencmd` – Raspberry-Pi-eigenes Tool (Teil von `libraspberrypi-bin`)
- `modprobe` – für RTC-Treiber-Reload bei direktem I2C-Zugriff

## Wichtige Hinweise zum DS3231

- I2C-Adresse: **0x68**
- Beim direkten smbus2-Zugriff muss der Kernel-Treiber (`rtc_ds1307`) vorher per `modprobe -r` entladen werden, sonst schlägt der Bus-Zugriff fehl (→ `rtc_wakeup_working_utc.py`)
- Der DS3231 speichert die Zeit in **UTC** – bei Alarm-Zeiten muss ggf. von lokaler Zeit umgerechnet werden
- `/boot/firmware/config.txt` muss `dtoverlay=i2c-rtc,ds3231` enthalten
