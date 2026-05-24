import os
import subprocess


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


class VcgencmdSensor:
    def read_temp_celsius(self) -> float:
        if _dev_mode():
            return 42.0
        # Ausgabe: "temp=45.0'C"
        out = subprocess.check_output(["vcgencmd", "measure_temp"], text=True)
        return float(out.strip().removeprefix("temp=").removesuffix("'C"))

    def read_voltage_volts(self) -> float:
        if _dev_mode():
            return 1.2
        # Ausgabe: "volt=1.2000V"
        out = subprocess.check_output(["vcgencmd", "measure_volts"], text=True)
        return float(out.strip().removeprefix("volt=").removesuffix("V"))