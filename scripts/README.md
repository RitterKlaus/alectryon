Raspberry bootet
      ↓
Netzwerkverbindung steht
      ↓
manage.sh wird ausgeführt
      ↓
git fetch → Update? → git pull
      ↓
python3 main.py startet

Timers:

Einrichten:
sudo systemctl daemon-reload
sudo systemctl enable --now measure.timer

Testen:
systemctl list-timers measure.timer
systemctl status measure.service
journalctl -u measure.service -n 50