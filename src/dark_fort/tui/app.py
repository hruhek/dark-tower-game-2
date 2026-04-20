from textual.app import App

from dark_fort.game.engine import GameEngine
from dark_fort.tui.screens import TitleScreen


class DarkFortApp(App):
    """Main Textual application for Dark Fort."""

    CSS_PATH = "styles.tcss"
    TITLE = "Dark Fort"

    def __init__(self) -> None:
        super().__init__()
        self.engine = GameEngine()

    def on_mount(self) -> None:
        self.push_screen(TitleScreen())
