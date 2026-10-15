from __future__ import annotations
import json
from pathlib import Path
from .modell import Energie, Held, rund


class OptolithFehler(Exception):
    """Fehlermeldung"""

EIGENSCHAFT_IDS = {
    "ATTR_1": "MU", "ATTR_2": "KL", "ATTR_3": "IN", "ATTR_4": "CH",
    "ATTR_5": "FF", "ATTR_6": "GE", "ATTR_7": "KO", "ATTR_8": "KK",
}

KAMPFTECHNIK_IDS = {
    "CT_1": "Armbrüste", 
    "CT_2": "Bögen", 
    "CT_3": "Dolche", 
    "CT_4": "Fechtwaffen",
    "CT_5": "Hiebwaffen", 
    "CT_6": "Kettenwaffen", 
    "CT_7": "Lanzen", 
    "CT_8": "Peitschen",
    "CT_9": "Raufen", 
    "CT_10": "Schilde", 
    "CT_11": "Schleudern", 
    "CT_12": "Schwerter",
    "CT_13": "Stangenwaffen", 
    "CT_14": "Wurfwaffen", 
    "CT_15": "Zweihandhiebwaffen",
    "CT_16": "Zweihandschwerter", 
    "CT_18": "Blasrohre", 
    "CT_19": "Diskusse"
}

SPEZIES = {
    "R_1": {"name": "Mensch",  "lep": 5, "sk": -5, "zk": -5, "gs": 8},
    "R_2": {"name": "Elf",     "lep": 2, "sk": -4, "zk": -6, "gs": 8},
    "R_3": {"name": "Halbelf", "lep": 4, "sk": -4, "zk": -6, "gs": 8},
    "R_4": {"name": "Zwerg",   "lep": 8, "sk": -4, "zk": -4, "gs": 6},
}


def laden(pfad: str | Path) -> Held:
    """Optolith lesen und umwandeln"""
    try:
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except OSError as e:
        raise OptolithFehler(f"Fehler: {e}") from e
    except json.JSONDecodeError as e:
        raise OptolithFehler(f"Keine gültige json Datei: {e}") from e
    return held_aus_optolith(daten)


def held_aus_optolith(daten: dict) -> Held:
    """Optolith data (dict) -> Held mit berechneten werten"""
    if not isinstance(daten, dict) or "attr" not in daten or "clientVersion" not in daten:
        raise OptolithFehler(
            "keine Optolith Heldendatei. "
        )

    spezies = SPEZIES.get(daten.get("r"), SPEZIES["R_1"])
    held = Held(name=daten.get("name", "Unbenannt"), profession="", spezies=spezies["name"])

    for eintrag in daten["attr"].get("values", []):
        kurz = EIGENSCHAFT_IDS.get(eintrag.get("id"))
        if kurz:
            held.eigenschaften[kurz] = eintrag.get("value", 8)
    e = held.eigenschaften

    lep = spezies["lep"] + 2 * e["KO"] + daten["attr"].get("lp", 0)
    held.energien["LeP"] = Energie(aktuell=lep, max=lep)

    held.grundwerte.update({
        "SK": spezies["sk"] + rund((e["MU"] + e["KL"] + e["IN"]) / 6),
        "ZK": spezies["zk"] + rund((e["KO"] + e["KO"] + e["KK"]) / 6),
        "AW": rund(e["GE"] / 2),
        "INI": rund((e["MU"] + e["GE"]) / 2),
        "GS": spezies["gs"],
        "WS": rund(e["KO"] / 2),
    })

    for kt_id, wert in daten.get("ct", {}).items():
        name = KAMPFTECHNIK_IDS.get(kt_id)
        if name:
            held.kampftechniken[name] = wert

    return held