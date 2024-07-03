[Deutsch](README.md) | [English](README.en.md)

# Discord Mensa Bot
Ein Discord Bot, der über das Angebot der Mensa am Adenauerring des Karlsruher Instituts für Technologie (KIT) informiert. Jeden Tag wird der aktuelle Speiseplan in Form eines Embeds in einen ausgewählten Channel gepostet und im Laufe des Tages aktualisiert.

## Befehle

### `/mensa embed days_ahead: x`
Zeigt das Mensa-Angebot x Tage im Voraus an. `days_ahead` ist optional.

### `/advanced home`
Postet einen Link zum Source Code des Bots.

### `/advanced ping`
Die Anwendung antwortet mit der Zeit (in Millisekunden), die sie benötigt hat, um den Befehl zu erhalten.

### `/advanced update`
Ein manuelles Update des Speiseplans wird angestoßen.

### `/advanced version`
Der aktuelle Git-Hash des Commits, auf dem die Anwendung läuft, wird ausgegeben.

## Aufsetzen

Das Projekt bietet ein fertiges Docker-Image als Package an. In der `docker-compose.yaml` gibt es eine beispielhafte Konfiguration. Diese Konfiguration muss mit folgenden Informationen ergänzt und gespeichert werden:

### Erforderliche Umgebungsvariablen:
- `BOT_TOKEN`: Dieser kann im [Discord Developer Portal](https://discord.com/developers/applications?new_application=true) erstellt werden.
- `GUILD`: Die Server-ID, auf dem der Bot laufen soll.
- `CHANNEL_ID`: Der Channel, in dem an Werktagen das Angebot der Mensa gepostet wird.

### Optionale Umgebungsvariablen:
- `UPDATE_INTERVAL`: Zeitintervall in Sekunden, nach dem das Angebot auf der Webseite der Mensa abgefragt und bei Änderungen im Embed auf Discord aktualisiert wird (Standard: 3600 Sekunden).

Dann kann die Anwendung mit dem Befehl `docker compose up -d` gestartet werden. Eine Anleitung zur Installation von Docker Compose findest du online.

## Entwickeln

Möchtest du etwas zum Projekt beitragen? Du kannst das Projekt von GitHub klonen und in einer virtuellen Umgebung (venv) ausführen. Schreibe die oben erwähnten Umgebungsvariablen in eine `.env` Datei und lege sie in das Verzeichnis.

Mit `pip install -r ./requirements.txt` kannst du die Abhängigkeiten installieren.

## Weitere Hinweise:
- Der Bot postet das Speiseangebot momentan immer um 9:30 Uhr.
- Der Bot kann in einem Announcement-Channel verwendet werden und veröffentlicht das Angebot dann auch an Server, die diesen Channel abonniert haben.
- Bitte ziehe in Erwägung, den Announcement-Channel des KIT Mathe-Info-Servers zu abonnieren und wenn nicht anders möglich, das Aktualisierungsintervall deiner Instanz nicht zu hoch zu setzen, um den Traffic auf www.sw-ka.de gering zu halten.
- Der Bot erstellt Logs, um Missbrauch zu vermeiden.
- Der Bot unterstützt nur moderne Slash Commands.
