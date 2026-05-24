import glob, time

# Alle angeschlossenen DS18B20-Sensoren finden
sensoren = glob.glob('/sys/bus/w1/devices/28-*')
print(f"{len(sensoren)} Sensor(en) gefunden:")
for s in sensoren:
    print(" ", s.split('/')[-1])

def read_temp(sensor_path):
    with open(sensor_path + '/w1_slave') as f:
        lines = f.readlines()
    if lines[0].strip()[-3:] == 'YES':
        return float(lines[1].split('t=')[1]) / 1000.0
    return None

while True:
    for i, sensor in enumerate(sensoren):
        temp = read_temp(sensor)
        sensor_id = sensor.split('/')[-1]
        print(f"Sensor {i+1} ({sensor_id}): {temp:.1f} °C")
    print("---")
    time.sleep(1)