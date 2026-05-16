#!/bin/bash
# /home/klaus/PROD/alectryon/scripts/manage.sh

REPO_DIR="/home/klaus/PROD/alectryon"
LOGFILE="/home/klaus/PROD/startup.log"

echo "=== Start: $(date) ===" >> "$LOGFILE"

# 1. Update holen
cd "$REPO_DIR"
git fetch origin >> "$LOGFILE" 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Update gefunden, ziehe Änderungen..." >> "$LOGFILE"
    git pull >> "$LOGFILE" 2>&1
else
    echo "Bereits aktuell." >> "$LOGFILE"
fi

# 2. Programm starten
echo "Starte Programm..." >> "$LOGFILE"
exec python3 "$REPO_DIR/app/main.py"