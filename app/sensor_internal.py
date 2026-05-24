import subprocess


class VcgencmdSensor:
    def read_temp_celsius(self) -> float:
        # Ausgabe: "temp=45.0'C"
        out = subprocess.check_output(["vcgencmd", "measure_temp"], text=True)
        return float(out.strip().removeprefix("temp=").removesuffix("'C"))

    def read_voltage_volts(self) -> float:
        # Ausgabe: "volt=1.2000V"
        out = subprocess.check_output(["vcgencmd", "measure_volts"], text=True)
        return float(out.strip().removeprefix("volt=").removesuffix("V"))