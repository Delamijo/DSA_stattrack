"""gui"""
from __future__ import annotations
from nicegui import ui
from .modell import Held, beispiel_held, EIGENSCHAFTEN, GRUNDWERTE

# theme
HINTERGRUND = "#14161b"
KARTE = "#1d2027"
LINIE = "#2c3039"
TEXT = "#ebe8e1"
NEBENTEXT = "#a9adb6"
AKZENT = "#e8b04a"

EIGENSCHAFT_FARBEN = {
    "MU": "#c0392b", "KL": "#8e44ad", "IN": "#27ae60", "CH": "#7f8c8d",
    "FF": "#d4b106", "GE": "#2e5fd1", "KO": "#9aa0a8", "KK": "#e67e22",
}

BUTTON_HOEHE = "44px"
RUNDUNG = "10px"


def _theme() -> None:
    """Theme und CSS overall"""
    ui.colors(primary=AKZENT)
    ui.query("body").style(f"background:{HINTERGRUND}; color:{TEXT}")
    ui.add_css(f"""
        .karte {{ background:{KARTE}; border-radius:{RUNDUNG}; padding:12px 14px; }}
        .q-btn {{ min-height:{BUTTON_HOEHE}; }}
        .zahl  {{ font-family:'IBM Plex Mono', monospace; }}
        .pm-knopf {{ background:#2a2e37 !important; border:1px solid #3a3f4a; border-radius:6px; min-width:40px; font-size:18px; }}
    """)


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
            with ui.column().classes("karte items-center gap-2").style(f"border-top:3px solid {farbe}"):
                ui.label(kurz).classes("text-sm font-semibold tracking-widest").style("color:#c9c6bf")
                _plus_minus(held.eigenschaften, kurz, minimum=0)


def _grundwerte(held: Held) -> None:
    with ui.grid(columns=3).classes("w-full gap-3"):
        for kurz, anzeigename in GRUNDWERTE.items():
            with ui.row().classes("karte items-center justify-between no-wrap"):
                ui.label(anzeigename).classes("text-sm").style("color:#c9c6bf")
                _plus_minus(held.grundwerte, kurz, schriftgroesse="22px")


# Build example
def baue_heldenbogen() -> None:
    held = beispiel_held()
    _theme()
    with ui.column().classes("w-full max-w-[1376px] mx-auto gap-5 p-6"):
        _kopfzeile(held)
        _eigenschaften(held)
        _grundwerte(held)