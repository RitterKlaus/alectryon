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

# damit man den RTC Alarm setzen kann
sudo usermod -a -G dialout klaus

SQW auch auf SCL GPIO 3 (PIN 5) verbinden.




