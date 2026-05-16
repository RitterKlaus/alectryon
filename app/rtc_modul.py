import smbus2
import struct
from datetime import datetime, timedelta

DS3231_ADDR = 0x68

# Register-Adressen
ALARM1_SEC    = 0x07
ALARM1_MIN    = 0x08
ALARM1_HOUR   = 0x09
ALARM1_DAY    = 0x0A
CONTROL_REG   = 0x0E
STATUS_REG    = 0x0F

def dec_to_bcd(val):
    return (val // 10) << 4 | (val % 10)

def set_alarm1(bus, wake_time: datetime):
    """Alarm 1 auf einen bestimmten Zeitpunkt setzen."""
    
    # Alarm-Register schreiben (A1M-Bits = 0 → Datum+Uhrzeit muss übereinstimmen)
    bus.write_byte_data(DS3231_ADDR, ALARM1_SEC,  dec_to_bcd(wake_time.second))
    bus.write_byte_data(DS3231_ADDR, ALARM1_MIN,  dec_to_bcd(wake_time.minute))
    bus.write_byte_data(DS3231_ADDR, ALARM1_HOUR, dec_to_bcd(wake_time.hour))
    bus.write_byte_data(DS3231_ADDR, ALARM1_DAY,  dec_to_bcd(wake_time.day) | 0x40)
    #                                                                           ↑
    #                                                   0x40 = DY/DT-Bit: Tag des Monats

    # Alarm-Flag löschen (Status-Register)
    status = bus.read_byte_data(DS3231_ADDR, STATUS_REG)
    bus.write_byte_data(DS3231_ADDR, STATUS_REG, status & ~0x01)

    # Alarm 1 im Control-Register aktivieren + INT/SQW-Pin aktivieren
    control = bus.read_byte_data(DS3231_ADDR, CONTROL_REG)
    control |= 0x01  # A1IE – Alarm 1 Interrupt ein
    control |= 0x04  # INTCN – SQW-Pin als Interrupt nutzen
    bus.write_byte_data(DS3231_ADDR, CONTROL_REG, control)

    print(f"Alarm gesetzt für: {wake_time}")

def schedule_wakeup(in_minuten=15):
    """Alarm setzen"""
    with smbus2.SMBus(1) as bus:
        # Default: in 15 Minuten aufwachen
        wake_time = datetime.now() + timedelta(minutes=in_minuten)
        set_alarm1(bus, wake_time)
