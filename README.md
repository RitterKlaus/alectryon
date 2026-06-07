# alectryon
Eine Anwendung, um verschiedene Sensoren energiesparend von einem Solar-betriebenen Raspberry Pi zu lesen.

## Installation

Das Skript benötigt sudo-Rechte. Bitte zuerst anschauen:

curl -fsSL https://raw.githubusercontent.com/RitterKlaus/alectryon/main/scripts/install.sh | less

dann ausführen:

curl -fsSL https://raw.githubusercontent.com/RitterKlaus/alectryon/main/scripts/install.sh | bash




## Hardware

1. Raspberry einrichten
2. Solar HAT, Akkus, Solarzelle verkabeln
i2c
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- 43 -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --  

3. RTC-Modul
    Verkabeln
    i2cdetect -y 1

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- 43 -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- 57 -- -- -- -- -- -- -- 5f 
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --  

siehe auch: https://raspberry.tips/raspberrypi-tutorials/rtc-ds1307-uhrzeit-raspberry-pi

sudo nano /boot/firmware/config.txt

Am Ende
# Für DS3231:
dtoverlay=i2c-rtc,ds3231

sudo reboot


Temperatursensoren an:
GND Pin 20
VCC Pin 17
DATA Pin 11 (GPIO 17)

1-wire Bus aktivieren für den Temperatursensor

# Standard (GPIO 4) — ersetzen durch:
dtoverlay=w1-gpio,gpiopin=17

Prüfen:
ls /sys/bus/w1/devices/
Dort sollten wieder deine 28-xxxx-Einträge erscheinen

raspi-config
Boot into Text Console einstellen!


# Immer an, Stromverbrauch minimieren
sudo nano /boot/firmware/config.txt
dtoverlay=disable-bt
Bluetooth Service abschalten
sudo systemctl disable bluetooth

### HDMI-Anschluss deaktivieren (/boot/firmware/config.txt)
dtoverlay=vc4-kms-v3d,nohdmi
hdmi_blanking=2

Raspberry WLAN Powersave eingeschaltet lassen
Wir probieren das mal. Eventuell schalten wir das WLAN abends ab und morgens wieder an.
Der Befehl braucht leider sudo



## Zurückgestellte Funktionen

Das Aufwecken per Alarm auf dem RTC-Modul ist aktuell nicht möglich.
Der Ausgang SQW müsste mit SCL GPIO 3 (PIN 5) verbunden werden. Nur dieser Pin kann zum Aufwecken verwendet werden. Der Pin ist aber vom I2C-Bus belegt. Der Raspberry Pi Zero kann zwar andere Pins für I2C nutzen, das wäre dann aber kein Hardware-unterstützter Bus. Ausßerdem ist das Solar-Modul über Pogo-Pins verbunden und benötigt den I2C-Bus an dieser Stelle.

Der Befehl rtcwake, den man im Internet findet, klappt außerdem nicht.

Ich habe mich daher entschieden, eine große Akku-Kapazität zu verwenden und den Stromverbrauch zu minimieren.

