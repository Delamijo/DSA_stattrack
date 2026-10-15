"""Datenmodell"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

# Konstanten
EIGENSCHAFTEN = ["MU", "KL", "IN", "CH", "FF", "GE", "KO", "KK"]

GRUNDWERTE = {
    "SK": "Seelenkraft",
    "ZK": "Zähigkeit",
    "AW": "Ausweichen",
    "INI": "Initiative",
    "GS": "Geschwindigkeit",
    "WS": "Wundschwelle",
}

ENERGIEN = {
    "LeP": "Lebensenergie",
    "AsP": "Astralenergie",
    "KaP": "Karmaenergie",
}

ZUSTAENDE = [
    "Animosität", "Begehren", "Belastung", "Berauscht", "Betäubung", "Entrückung",
    "Furcht", "Paralyse", "Schmerz", "Trance", "Überanstrengung", "Verwirrung",
]
MAX_ZUSTANDSSTUFE = 4

STATUS = [
    "Bewegungsunfähig", "Bewusstlos", "Blind", "Blutend", "Blutrausch", "Brennend",
    "Eingeengt", "Fixiert", "Handlungsunfähig", "Hörigkeit", "Krank", "Liegend",
    "Pechmagnet", "Raserei", "Stumm", "Taub", "Überrascht", "Übler Geruch",
    "Unsichtbar", "Vergiftet", "Versteinert",
]

KAMPFTECHNIKEN = {
    "Armbrüste":          {"leit": ("FF",),      "sf": "B", "fern": True,  "pa": False},
    "Bögen":              {"leit": ("FF",),      "sf": "C", "fern": True,  "pa": False},
    "Dolche":             {"leit": ("GE",),      "sf": "B", "fern": False, "pa": True},
    "Fechtwaffen":        {"leit": ("GE",),      "sf": "C", "fern": False, "pa": True},
    "Hiebwaffen":         {"leit": ("KK",),      "sf": "C", "fern": False, "pa": True},
    "Kettenwaffen":       {"leit": ("KK",),      "sf": "C", "fern": False, "pa": False},
    "Lanzen":             {"leit": ("KK",),      "sf": "B", "fern": False, "pa": True},
    "Raufen":             {"leit": ("GE", "KK"), "sf": "B", "fern": False, "pa": True},
    "Schilde":            {"leit": ("KK",),      "sf": "C", "fern": False, "pa": True},
    "Schleudern":         {"leit": ("FF",),      "sf": "B", "fern": True,  "pa": False},
    "Schwerter":          {"leit": ("GE", "KK"), "sf": "C", "fern": False, "pa": True},
    "Stangenwaffen":      {"leit": ("GE", "KK"), "sf": "C", "fern": False, "pa": True},
    "Wurfwaffen":         {"leit": ("FF",),      "sf": "B", "fern": True,  "pa": False},
    "Zweihandhiebwaffen": {"leit": ("KK",),      "sf": "C", "fern": False, "pa": True},
    "Zweihandschwerter":  {"leit": ("KK",),      "sf": "C", "fern": False, "pa": True},
}

KTW_START = 6

def bonus(wert: int) -> int:
    """+1 für 3 volle Punkte über 8 für AT, FK, PA"""
    return max(0, (wert - 8) // 3)

def rund(x: float) -> int:
    """nicht nativ runden (.5 zu 1)."""
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


# Blocks

@dataclass
class Energie:
    aktuell: int = 0
    max: int = 0

    def confirm(self, plus: int = 0, minus: int = 0) -> None:
        """Button "Bestätigen": aktuell + plus - minus"""
        self.aktuell = max(0, min(self.max, self.aktuell + plus - minus))

    def max_change(self, delta: int) -> None:
        """Max -/+"""
        self.max = max(0, self.max + delta)
        self.aktuell = min(self.aktuell, self.max)

    @property
    def anteil(self) -> float:
        """Fortschrittsbalken"""
        return self.aktuell / self.max if self.max > 0 else 0.0


@dataclass
class Nahkampfwaffe:
    name: str = ""
    kampftechnik: str = ""
    tp: str = ""
    at: int = 0
    pa: int = 0
    reichweite: str = ""
    angelegt: bool = False


@dataclass
class Fernkampfwaffe:
    name: str = ""
    kampftechnik: str = ""
    tp: str = ""
    fk: int = 0
    reichweite: str = ""
    ladezeit: str = ""
    angelegt: bool = False


@dataclass
class Ruestung:
    name: str = ""
    rs: int = 0
    be: int = 0
    angelegt: bool = False

@dataclass
class Eintrag:
    name: str = ""
    beschreibung: str = ""

# Held
@dataclass
class Held:
    name: str = "Neuer Held"
    profession: str = ""
    spezies: str = ""

    eigenschaften: dict[str, int] = field(default_factory=lambda: {k: 8 for k in EIGENSCHAFTEN})
    grundwerte: dict[str, int] = field(default_factory=lambda: {k: 0 for k in GRUNDWERTE})
    energien: dict[str, Energie] = field(default_factory=lambda: {k: Energie() for k in ENERGIEN})
    kampftechniken: dict[str, int] = field(default_factory=lambda: {k: KTW_START for k in KAMPFTECHNIKEN})

    schmerz_angekreuzt: list[bool] = field(default_factory=lambda: [False] * 5)

    nahkampf: list[Nahkampfwaffe] = field(default_factory=list)
    fernkampf: list[Fernkampfwaffe] = field(default_factory=list)
    ruestung: list[Ruestung] = field(default_factory=list)

    sonderfertigkeiten: list[Eintrag] = field(default_factory=list)
    zauber: list[Eintrag] = field(default_factory=list)

    zustaende: dict[str, int] = field(default_factory=lambda: {z: 0 for z in ZUSTAENDE})
    status: dict[str, bool] = field(default_factory=lambda: {s: False for s in STATUS})

    # Rules
    def schmerzschwellen(self) -> list[int]:
        """LeP schwellen Schmerz aus max LeP (40 -> 30/20/10/5/0)."""
        m = self.energien["LeP"].max
        return [rund(m * 3 / 4), rund(m / 2), rund(m / 4), 5, 0]

    def zustand_klicken(self, name: str, stufe: int) -> None:
        """Klick auf Stufe n setzt n"""
        aktuell = self.zustaende.get(name, 0)
        self.zustaende[name] = stufe - 1 if aktuell == stufe else stufe

    def kt_angriff(self, name: str) -> int:
        """AT Nahkampf MU bzw FK Fernkampf FF ohne mod"""
        ktw = self.kampftechniken[name]
        eigenschaft = "FF" if KAMPFTECHNIKEN[name]["fern"] else "MU"
        return ktw + bonus(self.eigenschaften[eigenschaft])

    def kt_parade(self, name: str) -> int | None:
        """PA mod; None wenn Kt keine PA hat"""
        info = KAMPFTECHNIKEN[name]
        if not info["pa"]:
            return None
        ktw = self.kampftechniken[name]
        leit = max(self.eigenschaften[e] for e in info["leit"])
        return (ktw + 1) // 2 + bonus(leit)

    # für json
    def to_dict(self) -> dict:
        """Held als dict"""
        return asdict(self)

    @classmethod
    def from_dict(cls, daten: dict) -> Held:
        """Dict -> Held"""
        held = cls()
        held.name = daten.get("name", held.name)
        held.profession = daten.get("profession", "")
        held.spezies = daten.get("spezies", "")

        held.eigenschaften.update(daten.get("eigenschaften", {}))
        held.grundwerte.update(daten.get("grundwerte", {}))
        for kurz, werte in daten.get("energien", {}).items():
            held.energien[kurz] = Energie(**werte)

        held.kampftechniken.update(daten.get("kampftechniken", {}))

        held.schmerz_angekreuzt = list(daten.get("schmerz_angekreuzt", held.schmerz_angekreuzt))

        held.nahkampf = [Nahkampfwaffe(**w) for w in daten.get("nahkampf", [])]
        held.fernkampf = [Fernkampfwaffe(**w) for w in daten.get("fernkampf", [])]
        held.ruestung = [Ruestung(**r) for r in daten.get("ruestung", [])]

        held.sonderfertigkeiten = [Eintrag(**e) for e in daten.get("sonderfertigkeiten", [])]
        held.zauber = [Eintrag(**e) for e in daten.get("zauber", [])]

        held.zustaende.update(daten.get("zustaende", {}))
        held.status.update(daten.get("status", {}))
        return held


# bsp
def beispiel_held() -> Held:
    held = Held(name="Hadruf der eisernen Hand", profession="Schaukämpfer", spezies="Mensch")
    held.eigenschaften.update({"MU": 15, "KL": 8, "IN": 13, "CH": 10, "FF": 10, "GE": 15, "KO": 16, "KK": 15})
    held.grundwerte.update({"SK": 1, "ZK": 3, "AW": 8, "INI": 15, "GS": 8, "WS": 9})
    held.kampftechniken.update({"Raufen": 15, "Schleudern": 12})
    held.energien["LeP"] = Energie(aktuell=40, max=40)
    held.nahkampf = [
        Nahkampfwaffe("Schlagring", "Raufen", "1W6+1", 17, 10, "kurz", True),
        Nahkampfwaffe("Schmiedehammer", "Hiebwaffen", "1W6+4", 8, 2, "mittel"),
        Nahkampfwaffe("Fackel", "Hiebwaffen", "1W6+1", 7, 3, "mittel"),
    ]
    held.fernkampf = [Fernkampfwaffe("Wurfkeule", "Wurfwaffen", "1W6+2", 6, "2/10/15", "1 Akt.", True)]
    held.ruestung = [Ruestung("Kettenhemd", 4, 2, True)]
    held.sonderfertigkeiten = [
        Eintrag("Finte", "Angriff mit Erschwernis, Gegner PA wird um selben Wert erschwert"),
        Eintrag("Wuchtschlag I", "AT -2, +2 TP."),
    ]
    held.zauber = [
        Eintrag("Feuerball", "AOE, der 1W6+3 Schaden verursacht."),
    ]
    return held