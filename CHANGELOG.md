# Changelog

- 2026-11-24 — Tobias Erlacher: `Argon2Field` merkt sich die Spaltengröße pro Model und Feld (`get_column_size()`), statt sie bei jedem geladenen Datensatz aus `information_schema` abzufragen; his `/service/account`: 1,05 s → 0,05 s. Nach Änderung der Spaltenbreite müssen Dienste neu geladen werden
- 2026-11-24 — Tobias Erlacher: `to_json()` ermittelt Feldfilter und Konverter nur noch einmal pro Model und Filter (`get_serializers()`) statt pro Datensatz; Ausgabe unverändert, sysmon `/checks`: 1,1 s → 0,45 s
- 2026-11-23 — Tobias Erlacher: `MySQLDatabase.execute_sql` nutzt offene Verbindungen weiter; neuer Helfer `connected(*databases)` hält eine Verbindung pro Block/Request offen (immobit-Liste: 2411 → 1 Verbindung zu openimmodb)
- 2026-07-29 — Tobias Erlacher: CHANGELOG eingeführt (Claude-Onboarding)
