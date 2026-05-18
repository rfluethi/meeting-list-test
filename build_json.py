#!/usr/bin/env python3
"""
Liest die Markdown-Tabelle aus sitzungen.md und erzeugt sitzungen.json.
Vergangene Sitzungen werden automatisch ausgefiltert.
"""

import json
import re
from datetime import datetime, date, timezone
from pathlib import Path

SOURCE = Path("sitzungen.md")
TARGET = Path("sitzungen.json")


def parse_markdown_table(text: str) -> list[dict]:
    """Findet die erste Markdown-Tabelle und gibt sie als Liste von Dicts zurück."""
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        return []

    # Erste Zeile = Header, zweite Zeile = Trennzeile (---), Rest = Daten
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def main():
    text = SOURCE.read_text(encoding="utf-8")
    rows = parse_markdown_table(text)

    heute = date.today()
    sitzungen = []

    for r in rows:
        # Datum parsen
        try:
            d = datetime.strptime(r["Datum"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue

        # Vergangene Sitzungen überspringen
        if d < heute:
            continue

        sitzungen.append({
            "datum": r["Datum"],
            "datum_formatiert": d.strftime("%d.%m.%Y"),
            "uhrzeit": r.get("Uhrzeit", ""),
            "titel": r.get("Titel", ""),
            "ort": r.get("Ort", ""),
            "beschreibung": r.get("Beschreibung", ""),
            "teilnehmer": r.get("Teilnehmer", ""),
        })

    # Nach Datum sortieren
    sitzungen.sort(key=lambda s: s["datum"])

    output = {
        "aktualisiert": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "anzahl": len(sitzungen),
        "sitzungen": sitzungen,
    }

    TARGET.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"{len(sitzungen)} Sitzungen nach {TARGET} geschrieben.")


if __name__ == "__main__":
    main()