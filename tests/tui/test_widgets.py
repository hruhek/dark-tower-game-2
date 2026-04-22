from textual.widgets import Label

from dark_fort.game.engine import GameEngine
from dark_fort.game.enums import Phase
from dark_fort.game.models import Armor, Player, Weapon
from dark_fort.game.tables import SHOP_ITEMS
from dark_fort.tui.app import DarkFortApp
from dark_fort.tui.widgets import CommandBar, LogView, StatusBar


class TestWidgets:
    async def test_status_bar_renders_with_player(self):
        player = Player(hp=15, max_hp=15, silver=18, points=5)
        player.weapon = Weapon(name="Warhammer", damage="d6")

        async with DarkFortApp().run_test() as pilot:
            bar = StatusBar(player=player, explored=3)
            pilot.app.screen.mount(bar)
            await pilot.pause()
            assert bar.player == player

    async def test_log_view_appends_messages(self):
        log = LogView()
        log.add_message("Test message 1")
        log.add_message("Test message 2")
        assert log.message_count == 2

    async def test_command_bar_shows_buttons(self):
        from dark_fort.game.enums import Command

        async with DarkFortApp().run_test() as pilot:
            bar = CommandBar()
            pilot.app.screen.mount(bar)
            await pilot.pause()
            bar.commands = [Command.ATTACK, Command.FLEE]
            await pilot.pause()
            assert len(bar.commands) == 2


class TestStatusBarArmor:
    async def test_status_bar_shows_armor(self):
        player = Player(hp=15, max_hp=15, silver=18, points=5)
        player.weapon = Weapon(name="Sword", damage="d6")
        player.armor = Armor(name="Armor", absorb="d4")

        async with DarkFortApp().run_test() as pilot:
            bar = StatusBar(player=player, explored=3)
            pilot.app.screen.mount(bar)
            await pilot.pause()
            armor_label = bar.query_one("#armor", Label)
            assert "Armor" in str(armor_label.content)

    async def test_status_bar_shows_no_armor(self):
        player = Player(hp=15, max_hp=15, silver=18, points=5)
        player.weapon = Weapon(name="Sword", damage="d6")

        async with DarkFortApp().run_test() as pilot:
            bar = StatusBar(player=player, explored=3)
            pilot.app.screen.mount(bar)
            await pilot.pause()
            armor_label = bar.query_one("#armor", Label)
            assert "None" in str(armor_label.content)


class TestDarkFortApp:
    async def test_app_starts_on_title_screen(self):
        async with DarkFortApp().run_test() as pilot:
            assert pilot.app.screen.__class__.__name__ == "TitleScreen"

    async def test_app_has_engine(self):
        async with DarkFortApp().run_test() as pilot:
            assert pilot.app.engine is not None  # ty: ignore[unresolved-attribute]


class TestGameScreen:
    async def test_game_screen_composes_widgets(self):
        engine = GameEngine()
        engine.start_game()
        async with DarkFortApp().run_test():
            pass


class TestShopScreen:
    async def test_shop_screen_exists(self):
        from dark_fort.tui.screens import ShopScreen

        engine = GameEngine()
        engine.start_game()
        engine.state.phase = Phase.SHOP
        engine.state.shop_wares = list(SHOP_ITEMS)
        screen = ShopScreen(engine=engine)
        assert screen is not None


class TestGameOverScreen:
    async def test_game_over_screen_exists(self):
        from dark_fort.tui.screens import GameOverScreen

        engine = GameEngine()
        engine.start_game()
        engine.state.player.hp = 0
        screen = GameOverScreen(engine=engine)
        assert screen is not None
