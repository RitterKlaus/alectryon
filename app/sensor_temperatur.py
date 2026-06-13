import os

W1_BASE = "/sys/bus/w1/devices"


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


class W1Sensoren:
    def read(self) -> dict:
        """
        Liest die konfigurierten DS18B20-Sensoren (SENSOR_INNEN, SENSOR_AUSSEN).
        Gibt nur die Schlüssel zurück, für die eine ID gesetzt ist.
        """
        if _dev_mode():
            return {"temp_innen": 18.5, "temp_aussen": 12.3}

        result = {}
        for key, env_var in [("temp_innen", "SENSOR_INNEN"),
                              ("temp_aussen", "SENSOR_AUSSEN")]:
            device_id = os.getenv(env_var)
            if device_id:
                result[key] = self._read_sensor(device_id)
        return result

    def _read_sensor(self, device_id: str) -> float:
        path = f"{W1_BASE}/{device_id}/w1_slave"
        with open(path) as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] != "YES":
            raise RuntimeError(f"CRC-Fehler bei Sensor {device_id}")
        return round(float(lines[1].split("t=")[1]) / 1000.0, 1)
