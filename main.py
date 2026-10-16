from pathlib import Path
from nicegui import ui
from nicegui import app as nicegui_app
from app.gui import baue_heldenbogen
import sys
import os
from multiprocessing import freeze_support


if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


BASIS = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
nicegui_app.add_static_files("/fonts", BASIS / "Fonts")

@ui.page("/")
def index() -> None:
    baue_heldenbogen()


if __name__ in {"__main__", "__mp_main__"}:
    freeze_support()
    ui.run(
        native=True,
        host="127.0.0.1",
        title="Heldenbogen",
        window_size=(1440, 900),
        dark=True,
        reload=False,
    )