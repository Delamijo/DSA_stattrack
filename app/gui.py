"""gui"""
from __future__ import annotations
from nicegui import ui
from .modell import Held, beispiel_held, EIGENSCHAFTEN, GRUNDWERTE, Energie, ENERGIEN, ZUSTAENDE, STATUS, MAX_ZUSTANDSSTUFE
from collections.abc import Callable

HINTERGRUND = "#14161b"
KARTE = "#1d2027"
LINIE = "#2c3039"
TEXT = "#ebe8e1"
NEBENTEXT = "#a9adb6"
AKZENT = "#e8b04a"

EIGENSCHAFT_FARBEN = {
    "MU": "#c0392b", 
    "KL": "#8e44ad", 
    "IN": "#27ae60", 
    "CH": "#7f8c8d",
    "FF": "#d4b106", 
    "GE": "#2e5fd1", 
    "KO": "#9aa0a8", 
    "KK": "#e67e22"
}

ENERGIE_FARBEN = {
    "LeP": "#d4453a", 
    "AsP": "#5b8fe0", 
    "KaP": "#d1a85a"
}

SCHMERZ_MARKIERUNG = "#3b2a12"

BUTTON_HOEHE = "44px"
RUNDUNG = "2px"
RAHMEN_BREITE = "2px"

SCHRIFT = "'Ubuntu', sans-serif"
SCHRIFT_ZAHLEN = "'Ubuntu Mono', monospace"


def _theme() -> None:
    """Theme und CSS overall"""
    ui.colors(primary=AKZENT)
    ui.query("body").style(f"background:{HINTERGRUND}; color:{TEXT}")
    ui.add_css(f"""
        /* --- Schriften aus dem Ordner fonts/ --- */
        @font-face {{ font-family:'Ubuntu'; font-weight:400; src:url('/fonts/Ubuntu-Regular.ttf'); }}
        @font-face {{ font-family:'Ubuntu'; font-weight:500; src:url('/fonts/Ubuntu-Medium.ttf'); }}
        @font-face {{ font-family:'Ubuntu'; font-weight:700; src:url('/fonts/Ubuntu-Bold.ttf'); }}
        @font-face {{ font-family:'Ubuntu Mono'; src:url('/fonts/UbuntuMono-Regular.ttf'); }}

        body  {{ font-family:{SCHRIFT}; }}
        .zahl {{ font-family:{SCHRIFT_ZAHLEN}; }}

        /* --- Kästen --- */
        .karte {{ background:{KARTE}; border:1px solid {LINIE};
                  border-radius:{RUNDUNG}; padding:12px 14px; }}

        /* --- Buttons --- */
        .q-btn {{ min-height:{BUTTON_HOEHE}; border-radius:{RUNDUNG} !important; }}
        .pm-knopf {{ background:#2a2e37 !important; border:1px solid #3a3f4a;
                     min-width:40px; font-size:18px; }}

        /* --- Eingabefelder --- */
        .q-field--outlined .q-field__control {{ border-radius:{RUNDUNG}; }}
    """)

SCHMERZ_TEXTE = [
    "¼ verloren · Schmerz +1",
    "½ verloren · Schmerz +1",
    "¾ verloren · Schmerz +1",
    "5 oder weniger · Schmerz +1",
    "0 oder weniger · im Sterben",
]
ROEMISCH = ["I", "II", "III", "IV"]

# Areas
def _kopfzeile(held: Held) -> None:
    with ui.row().classes("w-full items-center justify-between pb-4") \
            .style(f"border-bottom:1px solid {LINIE}"):
        with ui.row().classes("items-baseline gap-4"):
            ui.label(held.name).style(f"font-size:30px; color:{AKZENT}")
            ui.label(f"{held.profession} · {held.spezies}").style(f"color:{NEBENTEXT}")
        with ui.row().classes("gap-2"):
            ui.button("Optolith-JSON laden").props("outline no-caps color=white")
            ui.button("Stand laden").props("outline no-caps color=white")
            ui.button("Stand als JSON exportieren").props("unelevated no-caps text-color=black")

def _ueberschrift(text: str) -> None:
    """Goldene Bereichsüberschrift (Schmerz, Zustände, Status …)."""
    ui.label(text).classes("font-medium").style(f"font-size:20px; color:{AKZENT}")

def _plus_minus(werte: dict, schluessel: str, minimum: int | None = None, schriftgroesse: str = "28px") -> None:
    """+ - für Erigenschaft und Grund"""

    def aendern(delta: int) -> None:
        neu = werte[schluessel] + delta
        if minimum is not None:
            neu = max(minimum, neu)
        werte[schluessel] = neu

    with ui.row().classes("items-center gap-2 no-wrap"):
        ui.button("−", on_click=lambda: aendern(-1)).props("flat dense color=white").classes("pm-knopf")
        ui.label().bind_text_from(werte, schluessel, backward=str) \
            .classes("zahl text-center").style(f"min-width:40px; font-size:{schriftgroesse}")
        ui.button("+", on_click=lambda: aendern(+1)).props("flat dense color=white").classes("pm-knopf")


def _eigenschaften(held: Held) -> None:
    with ui.grid(columns=8).classes("w-full gap-3"):
        for kurz in EIGENSCHAFTEN:
            farbe = EIGENSCHAFT_FARBEN[kurz]
            with ui.column().classes("karte items-center gap-2").style(f"border:{RAHMEN_BREITE} solid {farbe}"):
                ui.label(kurz).classes("text-sm font-semibold tracking-widest").style("color:#c9c6bf")
                _plus_minus(held.eigenschaften, kurz, minimum=0)


def _grundwerte(held: Held) -> None:
    with ui.grid(columns=3).classes("w-full gap-3"):
        for kurz, anzeigename in GRUNDWERTE.items():
            with ui.row().classes("karte items-center justify-between no-wrap"):
                ui.label(anzeigename).classes("text-sm").style("color:#c9c6bf")
                _plus_minus(held.grundwerte, kurz, schriftgroesse="22px")

def _energie_karte(energie: Energie, name: str, farbe: str, nach_aenderung: Callable[[], None]) -> None:
    """Eine Karte: Kopf mit aktuell / max, Balken, Eingabe + / − und Bestätigen."""
    eingabe = {"plus": None, "minus": None}

    def bestaetigen() -> None:
        plus = int(eingabe["plus"] or 0)
        minus = int(eingabe["minus"] or 0)
        energie.confirm(plus, minus)
        eingabe["plus"] = None
        eingabe["minus"] = None
        nach_aenderung()

    def max_aendern(delta: int) -> None:
        energie.max_change(delta)
        nach_aenderung()

    with ui.column().classes("karte w-full gap-3"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(name).classes("text-base font-medium")
            with ui.row().classes("zahl items-center gap-2 no-wrap"):
                ui.label().bind_text_from(energie, "aktuell", backward=str).style("font-size:26px")
                ui.label("/").style(f"color:{NEBENTEXT}; font-size:18px")
                ui.button("−", on_click=lambda: max_aendern(-1)) \
                    .props("flat dense color=white").classes("pm-knopf")
                ui.label().bind_text_from(energie, "max", backward=str) \
                    .classes("text-center").style("font-size:20px; min-width:28px")
                ui.button("+", on_click=lambda: max_aendern(+1)) \
                    .props("flat dense color=white").classes("pm-knopf")
                ui.label("max").style(f"color:{NEBENTEXT}; font-size:12px")

        ui.linear_progress(show_value=False, size="16px", color=farbe) \
            .bind_value_from(energie, "anteil")

        with ui.row().classes("items-center gap-3"):
            ui.label("+").classes("zahl text-lg").style("color:#9fe0b5")
            ui.number(min=0, format="%d").bind_value(eingabe, "plus") \
                .props("outlined dense dark").classes("w-24")
            ui.label("−").classes("zahl text-lg").style("color:#ffb3a8")
            ui.number(min=0, format="%d").bind_value(eingabe, "minus") \
                .props("outlined dense dark").classes("w-24")
            ui.button("Bestätigen", on_click=bestaetigen) \
                .props("unelevated no-caps text-color=black")


def _energien(held: Held, nach_aenderung: Callable[[], None]) -> None:
    with ui.column().classes("w-full gap-3"):
        for kurz, name in ENERGIEN.items():
            _energie_karte(held.energien[kurz], name, ENERGIE_FARBEN[kurz], nach_aenderung)

@ui.refreshable
def _schmerz(held: Held) -> None:
    lep = held.energien["LeP"]
    schwellen = held.schmerzschwellen()

    with ui.column().classes("karte w-full gap-1"):
        _ueberschrift("Schmerz")
        ui.label(f"Schwellen aus max. LeP ({lep.max}). Erreichte Schwellen markiert") \
            .classes("text-xs pb-2").style(f"color:{NEBENTEXT}")
        for i, (schwelle, text) in enumerate(zip(schwellen, SCHMERZ_TEXTE)):
            _schmerz_zeile(held, i, schwelle, text, erreicht=lep.aktuell <= schwelle)


def _schmerz_zeile(held: Held, i: int, schwelle: int, text: str, erreicht: bool) -> None:
    hintergrund = SCHMERZ_MARKIERUNG if erreicht else "transparent"

    def umschalten(e) -> None:
        held.schmerz_angekreuzt[i] = e.value

    with ui.row().classes("w-full items-center no-wrap gap-3 px-2 py-1") \
            .style(f"background:{hintergrund}; border-top:1px solid {LINIE}"):
        ui.label(str(schwelle)).classes("zahl text-base").style("min-width:32px")
        ui.label(text).classes("text-sm grow")
        ui.checkbox(value=held.schmerz_angekreuzt[i], on_change=umschalten).props("dense")

@ui.refreshable
def _zustaende(held: Held) -> None:
    with ui.column().classes("karte w-full gap-2"):
        _ueberschrift("Zustände")
        # Spalten: Name (Rest) + je 44px pro Stufe
        with ui.grid(columns=f"1fr repeat({MAX_ZUSTANDSSTUFE}, 44px)") \
                .classes("w-full items-center gap-y-1"):
            # Kopfzeile
            ui.label("Zustand").classes("text-sm").style(f"color:{NEBENTEXT}")
            for r in ROEMISCH[:MAX_ZUSTANDSSTUFE]:
                ui.label(r).classes("text-sm text-center").style(f"color:{NEBENTEXT}")
            # eine Zeile pro Zustand
            for name in ZUSTAENDE:
                ui.label(name).classes("text-sm")
                for stufe in range(1, MAX_ZUSTANDSSTUFE + 1):
                    _zustand_feld(held, name, stufe)


def _zustand_feld(held: Held, name: str, stufe: int) -> None:
    def klicken() -> None:
        held.zustand_klicken(name, stufe)
        _zustaende.refresh()

    with ui.element("div").classes("flex justify-center"):
        ui.checkbox(value=held.zustaende[name] >= stufe, on_change=klicken).props("dense")

def _status(held: Held) -> None:
    with ui.column().classes("karte w-full gap-2"):
        _ueberschrift("Status")
        with ui.grid(columns=3).classes("w-full gap-x-4 gap-y-1"):
            for name in STATUS:
                ui.checkbox(name).bind_value(held.status, name).props("dense").classes("text-sm")

# Build example
def baue_heldenbogen() -> None:
    held = beispiel_held()
    _theme()
    with ui.column().classes("w-full max-w-[1376px] mx-auto gap-5 p-6"):
        _kopfzeile(held)
        _eigenschaften(held)
        _grundwerte(held)

        with ui.row().classes("w-full gap-5 items-start no-wrap"):
            with ui.column().style("flex:2 1 0; min-width:0"):
                _energien(held, nach_aenderung=_schmerz.refresh)
            with ui.column().style("flex:1 1 0; min-width:0"):
                _schmerz(held)

        with ui.row().classes("w-full gap-5 items-start no-wrap"):
            with ui.column().style("flex:1 1 0; min-width:0"):
                _zustaende(held)
            with ui.column().style("flex:1 1 0; min-width:0"):
                _status(held)