import smbus2
import subprocess
from datetime import datetime, timedelta, timezone

DS3231_ADDR = 0x68
ALARM1_SEC  = 0x07
ALARM1_MIN  = 0x08
ALARM1_HOUR = 0x09
ALARM1_DAY  = 0x0A
CONTROL_REG = 0x0E
STATUS_REG  = 0x0F

def dec_to_bcd(val):
    return (val // 10) << 4 | (val % 10)

def set_rtc_alarm(wake_time_local: datetime):
    # Lokale Zeit → UTC umrechnen
    wake_time_utc = wake_time_local.astimezone(timezone.utc)
    print(f"Alarm lokal: {wake_time_local.strftime('%H:%M:%S %Z')}")
    print(f"Alarm UTC:   {wake_time_utc.strftime('%H:%M:%S %Z')}")

    subprocess.run(["modprobe", "-r", "rtc_ds1307"], check=True)
    try:
        with smbus2.SMBus(1) as bus:
            status = bus.read_byte_data(DS3231_ADDR, STATUS_REG)
            bus.write_byte_data(DS3231_ADDR, STATUS_REG, status & ~0x01)

            bus.write_byte_data(DS3231_ADDR, ALARM1_SEC,  dec_to_bcd(wake_time_utc.second))
            bus.write_byte_data(DS3231_ADDR, ALARM1_MIN,  dec_to_bcd(wake_time_utc.minute))
            bus.write_byte_data(DS3231_ADDR, ALARM1_HOUR, dec_to_bcd(wake_time_utc.hour))
            bus.write_byte_data(DS3231_ADDR, ALARM1_DAY,  dec_to_bcd(wake_time_utc.day) | 0x40)

            control = bus.read_byte_data(DS3231_ADDR, CONTROL_REG)
            control |= 0x05
            bus.write_byte_data(DS3231_ADDR, CONTROL_REG, control)

            print(f"Alarm gesetzt!")
    finally:
        subprocess.run(["modprobe", "rtc_ds1307"], check=True)

# Aufruf mit lokaler Zeit – Umrechnung passiert automatisch
wake_time = datetime.now().astimezone() + timedelta(minutes=2)
set_rtc_alarm(wake_time)