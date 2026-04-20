from dark_fort.game.enums import Command, MonsterTier, Phase
from dark_fort.game.models import CombatState, Monster
from dark_fort.tui.app import DarkFortApp
from dark_fort.tui.widgets import CommandBar


class TestTitleScreen:
    async def test_pressing_enter_starts_game(self):
        async with DarkFortApp().run_test() as pilot:
            assert pilot.app.screen.__class__.__name__ == "TitleScreen"
            await pilot.press("enter")
            await pilot.pause()
            assert pilot.app.screen.__class__.__name__ == "GameScreen"
            log = pilot.app.screen.query_one("#log")
            assert log.message_count > 0  # ty: ignore[unresolved-attribute]

    async def test_starting_game_sets_exploring_phase(self):
        async with DarkFortApp().run_test() as pilot:
            await pilot.press("enter")
            await pilot.pause()
            assert pilot.app.engine.state.phase == Phase.EXPLORING  # ty: ignore[unresolved-attribute]


class TestGameScreenPhaseCommands:
    async def test_exploring_phase_shows_explore_and_inventory(self):
        async with DarkFortApp().run_test() as pilot:
            await pilot.press("enter")
            await pilot.pause()
            cmd_bar = pilot.app.screen.query_one("#commands", CommandBar)
            assert Command.EXPLORE in cmd_bar.commands
            assert Command.INVENTORY in cmd_bar.commands

    async def test_combat_phase_shows_attack_flee_use_item(self):
        async with DarkFortApp().run_test() as pilot:
            await pilot.press("enter")
            await pilot.pause()
            monster = Monster(
                name="Goblin", tier=MonsterTier.WEAK, points=3, damage="d4", hp=5
            )
            pilot.app.engine.state.combat = CombatState(monster=monster, monster_hp=5)  # ty: ignore[unresolved-attribute]
            pilot.app.engine.state.phase = Phase.COMBAT  # ty: ignore[unresolved-attribute]
            await pilot.pause()
            pilot.app.screen._update_commands()  # ty: ignore[unresolved-attribute]
            await pilot.pause()
            cmd_bar = pilot.app.screen.query_one("#commands", CommandBar)
            assert Command.ATTACK in cmd_bar.commands
            assert Command.FLEE in cmd_bar.commands
            assert Command.USE_ITEM in cmd_bar.commands

    async def test_shop_phase_shows_browse_and_leave(self):
        async with DarkFortApp().run_test() as pilot:
            await pilot.press("enter")
            await pilot.pause()
            pilot.app.engine.state.phase = Phase.SHOP  # ty: ignore[unresolved-attribute]
            await pilot.pause()
            pilot.app.screen._update_commands()  # ty: ignore[unresolved-attribute]
            await pilot.pause()
            cmd_bar = pilot.app.screen.query_one("#commands", CommandBar)
            assert Command.BROWSE in cmd_bar.commands
            assert Command.LEAVE in cmd_bar.commands
