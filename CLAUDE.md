# peeweeplus

## Architektur-Doku & Änderungs-Log (Pflicht)

Diese Regeln gelten für jede Claude-Session, die in diesem Repo arbeitet:

1. Nach JEDER abgeschlossenen Änderung einen Eintrag oben in `CHANGELOG.md`
   im Repo-Root anfügen (Datei anlegen, falls fehlt):
   `- YYYY-MM-DD — <Name>: <was geändert wurde, 1 Zeile>`
2. Betrifft die Änderung Zweck, Schnittstellen, Deployment oder Abhängigkeiten
   (neue/entfernte ORM-Modelle, öffentliche API/Funktionen, Console-Scripts, Python-Dependencies): zusätzlich `ARCHITECTURE.md` im Repo-Root aktualisieren, inkl.
   Kopfzeile „Stand: <Datum>, geprüft gegen Commit <sha>".
3. Vor dem Anlegen neuer Doku-Dateien IMMER prüfen, ob es zu dem Thema schon
   Doku gibt (`ARCHITECTURE.md`, `README.md`, `docs/`, zentrales Repo
   `homeinfo-architektur`) — Bestehendes ergänzen statt doppeln.
4. CHANGELOG-/ARCHITECTURE-Aktualisierungen mit in den Commit nehmen.
5. Niemals Zugangsdaten, Tokens oder Passwörter in Dateien oder Doku schreiben.
