# AGENTS.md

## Rules

- **NEVER** change `docs/DARK_FORT.md` — canonical game design document.

## Commands

```
make help     # list all targets
make test     # run pytest
make lint     # ruff check + format + ty check
```

Use `uv run <cmd>` for any direct command.

## Architecture

- `src/dark_fort/game/` — pure domain logic, zero Textual deps
- `src/dark_fort/tui/` — thin Textual layer, renders game state
- `game/` returns `ActionResult` Pydantic models; TUI calls engine methods and displays results

## Key files

- `game/engine.py` — `GameEngine` owns `GameState`, exposes all game actions
- `game/rules.py` — combat, flee, leveling, traps, scroll effects
- `game/tables.py` — all DARK_FORT reference tables as typed data
- `tui/screens.py` — TitleScreen, GameScreen, ShopScreen, GameOverScreen
- `tui/widgets.py` — StatusBar, LogView, CommandBar

## Testing

- `game/` tests: pure pytest, no Textual
- `tui/` tests: `DarkFortApp().run_test()` for async integration tests
- `asyncio_mode = "auto"` in pyproject.toml

## Ty suppressions

- `# ty: ignore[invalid-return-type]` on `game_app` properties (Textual's `self.app` returns `App[Unknown]`)
- `# ty: ignore[unresolved-attribute]` in test files for `pilot.app.engine`

