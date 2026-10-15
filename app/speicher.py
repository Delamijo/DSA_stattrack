"""Stand als JSON exportieren und laden"""
from __future__ import annotations

import json
from pathlib import Path

from .modell import Held

DATEIFORMAT_VERSION = 1


class SaveFail(Exception):
    """Fehlermeldung"""


def exportieren(held: Held, pfad: str | Path) -> None:
    """Held als json"""
    daten = {"version": DATEIFORMAT_VERSION, **held.to_dict()}
    text = json.dumps(daten, ensure_ascii=False, indent=2)
    Path(pfad).write_text(text, encoding="utf-8")


def laden(pfad: str | Path) -> Held:
    """Liest exportierte Datei"""
    try:
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except OSError as e:
        raise SaveFail(f"Fehler: Datei öffnen {e}") from e
    except json.JSONDecodeError as e:
        raise SaveFail(f"Keine json: {e}") from e

    if not isinstance(daten, dict) or "version" not in daten:
        raise SaveFail(
            "Kein Speicherstand dieser App "
            "Optolith json in „Optolith-JSON laden“ öffnen"
        )
    if daten["version"] != DATEIFORMAT_VERSION:
        raise SaveFail(f"Unbekannte Dateiversion {daten['version']}.")

    try:
        return Held.from_dict(daten)
    except (TypeError, ValueError) as e:
        raise SaveFail(f"Datei beschädigt: {e}") from e