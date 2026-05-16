import smbus2
import subprocess
import os
from datetime import datetime, timedelta

DS3231_ADDR = 0x68

ALARM1_SEC  = 0x07
ALARM1_MIN  = 0x08
ALARM1_HOUR = 0x09
ALARM1_DAY  = 0x0A
CONTROL_REG = 0x0E
STATUS_REG  = 0x0F

def dec_to_bcd(val):
    return (val // 10) << 4 | (val % 10)

def set_rtc_alarm(wake_time: datetime):
    # Treiber entladen
    subprocess.run(["modprobe", "-r", "rtc_ds1307"], check=True)
    
    try:
        with smbus2.SMBus(1) as bus:
            # Alarm-Flag löschen
            status = bus.read_byte_data(DS3231_ADDR, STATUS_REG)
            bus.write_byte_data(DS3231_ADDR, STATUS_REG, status & ~0x01)

            # Alarmzeit schreiben
            bus.write_byte_data(DS3231_ADDR, ALARM1_SEC,  dec_to_bcd(wake_time.second))
            bus.write_byte_data(DS3231_ADDR, ALARM1_MIN,  dec_to_bcd(wake_time.minute))
            bus.write_byte_data(DS3231_ADDR, ALARM1_HOUR, dec_to_bcd(wake_time.hour))
            bus.write_byte_data(DS3231_ADDR, ALARM1_DAY,  dec_to_bcd(wake_time.day) | 0x40)

            # Alarm 1 + Interrupt aktivieren
            control = bus.read_byte_data(DS3231_ADDR, CONTROL_REG)
            control |= 0x05  # A1IE + INTCN
            bus.write_byte_data(DS3231_ADDR, CONTROL_REG, control)

            print(f"Alarm gesetzt für: {wake_time}")
    finally:
        # Treiber wieder laden
        subprocess.run(["modprobe", "rtc_ds1307"], check=True)

wake_time = datetime.now() + timedelta(minutes=2)
set_rtc_alarm(wake_time)