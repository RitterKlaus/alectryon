#!/bin/bash
# /home/klaus/PROD/alectryon/scripts/install.sh

# TODO
# Das Skript geht davon aus, dass der User "klaus" heißt.

# Der Benutzer muss vorher folgendes tun:
# git muss vorhanden sein

# I2C aktivieren (falls noch nicht):
# sudo raspi-config  # → Interface Options → I2C → Enable

# Prüfen ob das Modul erkannt wird (Adresse 0x68):
# i2cdetect -y 1

#sudo visudo
# pi ALL=(ALL) NOPASSWD: /sbin/shutdown

# Jetzt kann es losgehen

# Bibliothek installieren:
#pip install smbus2

set -e  # Abbruch bei jedem Fehler

INSTALL_DIR="/home/klaus/PROD"
REPO_DIR="$INSTALL_DIR/alectryon"
SERVICE_NAME="alectryon"

echo "=== Installation startet: $(date) ==="

# 1. Verzeichnis anlegen (nur wenn nicht vorhanden)
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 2. Repo klonen (oder updaten falls schon vorhanden)
if [ -d "$REPO_DIR/.git" ]; then
    echo "Repo existiert bereits, führe git pull durch..."
    cd "$REPO_DIR" && git pull
else
    echo "Klone Repository..."
    git clone https://github.com/RitterKlaus/alectryon.git
fi

# 3. Service installieren
echo "Installiere systemd-Service..."
sudo cp "$REPO_DIR/scripts/$SERVICE_NAME.service" /etc/systemd/system/
sudo systemctl daemon-reload   # ← wichtig nach jeder .service-Änderung
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# 4. Nach dem git clone: Prüfen ob .env existiert
if [ ! -f "$REPO_DIR/app/.env" ]; then
    cp "$REPO_DIR/app/.env.example" "$REPO_DIR/app/.env" 
    echo ""
    echo "    Bitte Werte in die .env Datei eintragen:"
    echo "    nano $REPO_DIR/app/.env"
    echo ""
fi

# 5. Status prüfen
echo "=== Installation abgeschlossen ==="
sudo systemctl status "$SERVICE_NAME" --no-pager

# Ab jetzt hält sich das System selbst aktuell, in dem es neue Versionen von git lädt.









