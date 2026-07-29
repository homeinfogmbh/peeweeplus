# peeweeplus
Stand: 2026-07-29, geprüft gegen Commit 02dea15

## Zweck
Praktische Erweiterung des Peewee-ORM. Liefert zusätzliche Feldtypen,
JSON-(De)Serialisierung von Modellen, einen konfigurierbaren MySQL-Datenbank-
Proxy und diverse Hilfen — die gemeinsame ORM-Grundlage aller Homeinfo-
Datenbank-Komponenten.

## Stack & Einstiegspunkte
Python 3, aufbauend auf `peewee`. Package `peeweeplus` mit Subpackages
`peeweeplus.fields` und `peeweeplus.json`. Wichtige Module: `database.py`,
`dbproxy.py` (`MySQLDatabaseProxy`), `model.py` (`JSONModel`), `mixins.py`,
`converters.py`, `introspection.py`, `html.py`, `transaction.py`,
`contextmanagers.py`, `types.py`, `exceptions.py`.

## Schnittstellen
### Konsumiert
- **Dependencies:** `peewee`, `configlib` (DB-Config), `lxml`, `python-magic`.

### Bietet an
- `MySQLDatabaseProxy` (verzögerte, konfigurierte DB-Anbindung — von `hwdb`,
  `mdb`, `sysmon`, `termgr` genutzt: `MySQLDatabaseProxy("<name>")`).
- `JSONModel` (Peewee-Model mit `to_json`/JSON-Mapping), zusätzliche Felder
  (u. a. Enum-, IPv6-, HTML-Text-Felder) und Transaktions-/Introspektions-Helfer.

## Deployment / Laufzeit
Reine Bibliothek; von den ORM-nutzenden Komponenten importiert. Kein Dienst.
DB-Zugangsdaten kommen zur Laufzeit aus den `configlib`-Konfigurationen der
jeweiligen Anwendung (außerhalb dieses Repos).

## Ersetzbarkeit
Kopplungsgrad: **hoch (zentral)**. Das gesamte Datenmodell des Homeinfo-Stacks
(`mdb`, `hwdb`, `sysmon` u. a.) basiert auf `JSONModel` und `MySQLDatabaseProxy`.
Signatur-/Verhaltensänderungen wirken breit; isoliert kaum ersetzbar.

## Weitere Doku
- `README.md` (Verweis auf das zugrundeliegende peewee-Framework).
- ⚠️ ANNAHME: Zentrales Repo `homeinfo-architektur` (Ordner `komponenten/`) noch
  nicht geprüft.
