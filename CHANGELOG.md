# Changelog

- 2026-11-24 — Tobias Erlacher: `to_json()` ermittelt Feldfilter und Konverter nur noch einmal pro Model und Filter (`get_serializers()`) statt pro Datensatz; Ausgabe unverändert, sysmon `/checks`: 1,1 s → 0,45 s
- 2026-11-23 — Tobias Erlacher: `MySQLDatabase.execute_sql` nutzt offene Verbindungen weiter; neuer Helfer `connected(*databases)` hält eine Verbindung pro Block/Request offen (immobit-Liste: 2411 → 1 Verbindung zu openimmodb)
- 2026-07-29 — Tobias Erlacher: CHANGELOG eingeführt (Claude-Onboarding)
