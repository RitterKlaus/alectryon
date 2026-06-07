import os
import smbus2

# Pi Zero UPS HAT (B) – INA219 Chip
# I2C-Adresse des Boards: 0x43
# Kalibrierung: 16V / 5A, Shunt 0.01 Ohm

INA219_ADDR     = 0x43

_REG_CONFIG      = 0x00
_REG_SHUNTVOLT   = 0x01
_REG_BUSVOLT     = 0x02
_REG_POWER       = 0x03
_REG_CURRENT     = 0x04
_REG_CALIBRATION = 0x05

# Kalibrierungswerte für 16V / 5A (aus Hersteller-Demo)
_CAL_VALUE   = 26868
_CURRENT_LSB = 0.1524   # mA pro Bit
_POWER_LSB   = 0.003048 # W pro Bit

# Konfiguration: 16V-Bereich, Gain /2 (80mV), 12bit 32 Samples, kontinuierlich
_CONFIG = (
    0b00 << 13 |  # VBUS_MAX 16V
    0b01 << 11 |  # Gain /2, 80mV
    0x0D <<  7 |  # Bus ADC: 12bit, 32 Samples
    0x0D <<  3 |  # Shunt ADC: 12bit, 32 Samples
    0x07          # Modus: Shunt + Bus kontinuierlich
)


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


def _read(bus, reg: int) -> int:
    data = bus.read_i2c_block_data(INA219_ADDR, reg, 2)
    return (data[0] << 8) | data[1]


def _write(bus, reg: int, value: int) -> None:
    bus.write_i2c_block_data(INA219_ADDR, reg, [value >> 8, value & 0xFF])


def _init(bus) -> None:
    _write(bus, _REG_CALIBRATION, _CAL_VALUE)
    _write(bus, _REG_CONFIG, _CONFIG)


class UsvSensor:
    def read(self) -> dict:
        """
        Liefert ein Dict mit:
          spannung_v   – Akkuspannung in Volt
          strom_ma     – Strom in mA (positiv = laden, negativ = entladen)
          leistung_w   – Leistung in Watt
          ladestand_pz – geschätzter Ladestand in Prozent (0–100)
        """
        if _dev_mode():
            return {
                "spannung_v":   3.85,
                "strom_ma":     120.0,
                "leistung_w":   0.46,
                "ladestand_pz": 71,
            }

        with smbus2.SMBus(1) as bus:
            _init(bus)

            # Busspannung (Akkuseite)
            raw_bus = _read(bus, _REG_BUSVOLT)
            spannung_v = (raw_bus >> 3) * 0.004

            # Shunt-Strom
            _write(bus, _REG_CALIBRATION, _CAL_VALUE)
            raw_cur = _read(bus, _REG_CURRENT)
            if raw_cur > 32767:
                raw_cur -= 65536
            strom_ma = raw_cur * _CURRENT_LSB

            # Leistung
            _write(bus, _REG_CALIBRATION, _CAL_VALUE)
            raw_pwr = _read(bus, _REG_POWER)
            if raw_pwr > 32767:
                raw_pwr -= 65536
            leistung_w = raw_pwr * _POWER_LSB

            # Ladestand: Formel aus Hersteller-Demo (3.0V = 0%, 4.2V = 100%)
            ladestand_pz = round((spannung_v - 3.0) / 1.2 * 100)
            ladestand_pz = max(0, min(100, ladestand_pz))

        return {
            "spannung_v":   round(spannung_v, 3),
            "strom_ma":     round(strom_ma, 1),
            "leistung_w":   round(leistung_w, 3),
            "ladestand_pz": ladestand_pz,
        }
