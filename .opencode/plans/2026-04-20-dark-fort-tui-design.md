# Dark Fort TUI — Design Spec

## Overview

A faithful digital adaptation of the DARK FORT solo dungeon-crawler game, built as a terminal TUI using Textual. The game preserves the dice-and-paper experience while automating bookkeeping and presenting it through a clean, modern terminal interface.

## Architecture

### Layer Structure

```
dark-tower-game-2/
├── src/
│   └── dark_fort/
│       ├── __init__.py
│       ├── __main__.py              # Thin bootstrap: from dark_fort.cli import main; main()
│       ├── cli.py                   # Entry point logic: main(), argument parsing
│       ├── game/                    # Pure domain logic — zero Textual deps
│       │   ├── __init__.py
│       │   ├── dice.py              # Dice engine (roll, d4, d6, expression parser)
│       │   ├── models.py            # Pydantic schemas: Player, Monster, Item, Room, GameState
│       │   ├── enums.py             # All game enums: Phase, ItemType, Command, etc.
│       │   ├── tables.py            # DARK_FORT tables: monsters, items, scrolls, shop, room shapes
│       │   ├── engine.py            # Game loop: state transitions, room generation, combat resolution
│       │   └── rules.py             # Combat logic, leveling, flee, traps, scroll effects
│       └── tui/                     # Textual layer — thin, renders game state
│           ├── __init__.py
│           ├── app.py               # Main App class, screen routing
│           ├── screens.py           # TitleScreen, GameScreen, ShopScreen, GameOverScreen
│           ├── widgets.py           # LogView, StatusBar, CommandBar
│           └── styles.tcss          # Textual CSS styling
├── tests/
│   ├── game/                # Fast unit tests for all game logic
│   │   ├── test_dice.py
│   │   ├── test_models.py
│   │   ├── test_rules.py
│   │   └── test_engine.py
│   └── tui/                 # Textual integration tests
│       ├── test_screens.py
│       └── test_widgets.py
├── docs/
│   ├── DARK_FORT.md         # NEVER CHANGE
│   ├── screen-mocks.md      # Widget trees + layout descriptions
│   └── superpowers/specs/
│       └── 2026-04-20-dark-fort-tui-design.md
└── pyproject.toml           # [project.scripts] dark-fort = "dark_fort.cli:main"
```

### Data Flow

1. `engine.py` owns `GameState` and exposes methods: `enter_room()`, `attack()`, `flee()`, `buy_item()`, etc.
2. Each method returns an `ActionResult` (Pydantic model with `messages`, `phase`, `choices`, `state_delta`)
3. TUI screens call engine methods, display messages in the scrolling log, update status bar reactively
4. Engine is completely unaware of Textual — pure Python, fully testable with pytest

## Models (Pydantic + Enums)

### Enums

```python
from enum import StrEnum

class ItemType(StrEnum):
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    SCROLL = auto()
    ROPE = auto()
    CLOAK = auto()

class MonsterTier(StrEnum):
    WEAK = auto()
    TOUGH = auto()

class Phase(StrEnum):
    TITLE = auto()
    ENTRANCE = auto()
    EXPLORING = auto()
    COMBAT = auto()
    SHOP = auto()
    GAME_OVER = auto()
    VICTORY = auto()

class Command(StrEnum):
    ATTACK = auto()
    FLEE = auto()
    USE_ITEM = auto()
    EXPLORE = auto()
    INVENTORY = auto()
    MOVE = auto()
    BROWSE = auto()
    LEAVE = auto()
    BUY = auto()

class ScrollType(StrEnum):
    SUMMON_DAEMON = auto()
    SOUTHERN_GATE = auto()
    AEGIS_OF_SORROW = auto()
    FALSE_OMEN = auto()
```

### Core Schemas

```python
class Weapon(BaseModel):
    name: str
    damage: str          # e.g. "d6", "d4", "d6+1"
    attack_bonus: int = 0

class Item(BaseModel):
    name: str
    type: ItemType
    damage: str | None = None
    attack_bonus: int = 0
    uses: int | None = None

class Monster(BaseModel):
    name: str
    tier: MonsterTier
    points: int
    damage: str
    hp: int
    loot: str | None = None
    special: str | None = None

class Player(BaseModel):
    name: str = "Kargunt"
    hp: int = 15
    max_hp: int = 15
    silver: int = 0
    points: int = 0
    weapon: Weapon | None = None
    armor: bool = False
    inventory: list[Item] = []
    scrolls: list[Item] = []
    cloak_charges: int = 0
    attack_bonus: int = 0
    level_benefits: list[int] = []  # scratched-off benefit IDs (1-6), unique enforced by validator
    daemon_fights_remaining: int = 0

class Room(BaseModel):
    id: int
    shape: str
    doors: int
    result: str
    explored: bool = False
    connections: list[int] = []

class CombatState(BaseModel):
    monster: Monster
    monster_hp: int
    player_turns: int = 0
    daemon_assist: bool = False

class GameState(BaseModel):
    player: Player
    current_room: Room | None = None
    rooms: dict[int, Room] = {}
    phase: Phase
    combat: CombatState | None = None
    level_up_queue: bool = False
    log: list[str] = []

class ActionResult(BaseModel):
    messages: list[str]
    phase: Phase | None = None
    choices: list[Command] = []
    state_delta: dict[str, Any] = {}
```

## Screens

### Title Screen

```
Screen: TitleScreen
├── Container (align: center middle)
│   ├── Header (static) — "DARK FORT" — large centered text
│   ├── Subtitle (static) — "A delve into the catacombs"
│   └── Footer — "Press ENTER to begin"
```

### Game Screen (Main Gameplay)

```
Screen: GameScreen
├── Vertical (dock: top)
│   └── StatusBar
│       ├── "HP: 15/15"
│       ├── "Silver: 18"
│       ├── "Points: 5"
│       ├── "Rooms: 3/12"
│       └── "Weapon: Warhammer (d6)"
├── LogView (scrollable, fills remaining space)
│   └── RichLog — append-only event log
│       ├── "You enter a square room with two doors."
│       ├── "A Blood-Drenched Skeleton stands guard!"
│       └── "Rolling to hit... you rolled 4, need 3. HIT!"
└── CommandBar (dock: bottom)
    └── Horizontal buttons (context-sensitive)
        ├── [Attack] [Flee] [Use Item]  (during combat)
        ├── [Explore] [Inventory] [Move North] [Move South]  (in room)
        └── [Browse] [Leave]  (in shop)
```

### Shop Screen (Void Peddler)

```
Screen: ShopScreen
├── Vertical
│   ├── Header — "The Void Peddler"
│   ├── ShopList (scrollable)
│   │   └── Table: Item | Price | [Buy]
│   │       ├── Potion (d6 heal)     | 4s  | [1]
│   │       ├── Random scroll        | 7s  | [2]
│   │       └── ...
│   └── Footer — "Silver: 18 | Press number to buy, L to leave"
```

### Game Over Screen

```
Screen: GameOverScreen
├── Container (align: center middle)
│   ├── Header — "YOU HAVE FALLEN"
│   ├── Stats
│   │   ├── "Rooms explored: 7"
│   │   ├── "Monsters slain: 4"
│   │   └── "Points gathered: 12/15"
│   └── Footer — "Press ENTER to try again"
```

### Screen Transitions

```
TitleScreen → GameScreen (entrance room generated)
GameScreen → ShopScreen (room roll = 6)
ShopScreen → GameScreen (player leaves)
GameScreen → GameOverScreen (HP = 0)
GameScreen → VictoryScreen (level up + all benefits claimed)
GameOverScreen → TitleScreen (restart)
```

## Testing Strategy

### Game Logic Tests (`tests/game/`)

Pure pytest — no Textual dependency.

- `test_dice.py` — roll ranges, expression parsing (`d6+1`, `d4×d6`)
- `test_rules.py` — combat hit/miss, armor, flee damage, leveling conditions, scroll effects, traps
- `test_engine.py` — room generation, shop opening, purchases, game over, victory
- `test_models.py` — Pydantic validation, serialization/deserialization

### TUI Tests (`tests/tui/`)

Textual `App.run_test()` for integration testing.

- `test_screens.py` — title → game transition, combat buttons appear, shop purchase flow, game over
- `test_widgets.py` — status bar reactive updates, log message appending

### Coverage Goal

- `game/` — 90%+ (every rule, table entry, edge case)
- `tui/` — smoke tests for screen transitions and command routing

## Error Handling

- **Engine level** — Pydantic validation catches bad state. Invalid actions return error messages in `ActionResult.messages`. No exceptions bubble up.
- **TUI level** — Command bar prevents invalid actions by being context-sensitive. Error messages displayed in log. No crashes from bad input.
- **Save/Load** — `GameState.model_dump_json()` / `model_validate_json()`. Invalid data returns to title with error log.

## Dice Mechanics

All dice rolls are auto-generated by the engine with narrative reveal in the log. The dice engine (`game/dice.py`) supports:

- Single dice: `d4`, `d6`
- Modified dice: `d6+1`, `d6+2`
- Multi-dice: `3d6`, `d4×d6`
- Probability helpers: `X-in-6` checks
