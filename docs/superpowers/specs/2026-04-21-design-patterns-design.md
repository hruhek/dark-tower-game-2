# Design: Apply Design Patterns for Maintainability

## Date

2026-04-21

## Context

Dark Fort is a single-player TUI dungeon crawl (~1,400 LOC). The `game/` module contains pure domain logic (engine, rules, models, tables), and `tui/` contains Textual screens/widgets. The codebase has three categories of maintainability pain:

1. **Stringly-typed data** — room events and monster specials use bare strings; typos are invisible and handlers are scattered.
2. **Item behavior scattering** — `isinstance` chains and `match/case` blocks for items appear in `engine.py` and `screens.py`; adding an item type requires touching 4+ locations.
3. **Phase/command coupling** — `GameScreen` hard-codes which commands are available in each phase and how to dispatch them; adding a new phase requires changes in multiple files.

## Goals

- Adding a new item type should require changing **one file** (the item subclass).
- Adding a new room event or monster special should be **type-safe** (no invisible string typos).
- Adding a new phase should require a **single new class**, not scattered conditionals.
- No change to existing tests unless the test was directly testing an implementation detail that moved.

## Approach

Three independent but complementary refactors, applied in order:

1. **Enumify room events and monster specials**
2. **Strategy pattern for items** (`use()` and `display_stats()` methods on `Item` subclasses)
3. **State pattern for phases** (`PhaseState` classes that own commands and dispatch)

---

## 1. Enum-Based Room Events & Monster Specials

### Problem

`ROOM_RESULTS` is `list[str]`. `resolve_room_event` matches on string literals (`"Pit trap"`, `"Riddling Soothsayer"`, etc.). Monster `special` fields are also strings (`"death_ray_1_in_6"`). Adding a new event or special requires editing a table in `tables.py` AND adding an `elif` branch in `rules.py` — easy to miss one.

### Solution

Introduce `RoomEvent(StrEnum)` and `MonsterSpecial(StrEnum)` in `enums.py`.

```python
class RoomEvent(StrEnum):
    EMPTY = "Nothing. Explored."
    PIT_TRAP = "Pit trap"
    SOOTHSAYER = "Riddling Soothsayer"
    WEAK_MONSTER = "Weak monster"
    TOUGH_MONSTER = "Tough monster"
    SHOP = "Void Peddler"

class MonsterSpecial(StrEnum):
    LOOT_DAGGER = "loot_dagger_2_in_6"
    LOOT_SCROLL = "loot_scroll_2_in_6"
    LOOT_ROPE = "loot_rope_2_in_6"
    DEATH_RAY = "death_ray_1_in_6"
    PETRIFY = "petrify_1_in_6"
    INSTANT_LEVEL_UP = "instant_level_up_2_in_6"
    SEVEN_POINTS_ON_KILL = "7_points_on_kill"
```

`ROOM_RESULTS` becomes `list[RoomEvent]`. `Monster.special` becomes `MonsterSpecial | None`. `resolve_room_event` and `resolve_monster_special` dispatch on enum members.

### Impact

- Type checker catches typos.
- IDE navigation works (Cmd+click on `RoomEvent.PIT_TRAP` jumps to table entry and handler).
- Adding a new event/special requires adding the enum member AND its handler — the type system forces the handler, not human memory.

### Files changed

- `game/enums.py` — add `RoomEvent`, `MonsterSpecial`
- `game/tables.py` — `ROOM_RESULTS` type, `Monster` model field
- `game/rules.py` — match on enum members instead of strings

---

## 2. Item Strategy Pattern

### Problem

Item behavior is scattered across `engine.py` and `screens.py` in large `match`/`isinstance` chains:
- `engine.use_item()` (lines 192-233): `match item:` block
- `engine.buy_item()` (lines 150-172): another `match item:` block
- `screens._show_inventory()` (lines 123-151): `isinstance` chain for display labels
- `ShopScreen.on_mount()` (lines 190-201): `isinstance` chain for display stats

Adding a new item type means touching 4+ locations across 2 modules.

### Solution

Add behavior methods directly to each `Item` subclass (Pydantic models):

```python
class Item(BaseModel):
    name: str

    def use(self, state: GameState, index: int) -> ActionResult:
        raise NotImplementedError

    def display_stats(self) -> str:
        return ""

class Weapon(Item):
    type: Literal[ItemType.WEAPON] = ItemType.WEAPON
    damage: str
    attack_bonus: int = 0

    def display_stats(self) -> str:
        stats = self.damage
        if self.attack_bonus:
            stats += f"/+{self.attack_bonus}"
        return stats

    def use(self, state: GameState, index: int) -> ActionResult:
        messages = []
        player = state.player
        if player.weapon is not None:
            player.inventory.append(player.weapon)
            messages.append(f"{player.weapon.name} moved to inventory.")
        player.weapon = self
        messages.append(f"You equip the {self.name}.")
        player.inventory.pop(index)
        return ActionResult(messages=messages)
```

(Potion, Armor, Scroll, Cloak, Rope each get analogous methods.)

### Impact

- `engine.use_item()` collapses to ~10 lines: validate index, delegate to `item.use()`.
- TUI replaces `isinstance` chains with `item.display_stats()`.
- `engine.buy_item()` stays slightly longer because placement (slot vs inventory) is engine policy, but can be simplified with an `equip_slot` property on `Item` if desired later.

### Files changed

- `game/models.py` — add `use()` and `display_stats()` to `Item` and subclasses
- `game/engine.py` — simplify `use_item`, `buy_item`
- `tui/screens.py` — replace `isinstance` chains in `_show_inventory` and `ShopScreen`

---

## 3. Phase State Pattern

### Problem

Phase behavior is scattered:
- `GameScreen._update_commands` has a phase→commands mapping
- `GameScreen._handle_command` has a phase→action mapping
- `engine.py` has phase-specific logic intermixed

Adding a new phase (e.g., `LEVEL_UP`) requires changes in engine, screens, and widgets.

### Solution

Introduce a `PhaseState` ABC and concrete implementations for each phase:

```python
# game/phase_states.py

class PhaseState(ABC):
    @property
    @abstractmethod
    def phase(self) -> Phase: ...

    @property
    @abstractmethod
    def available_commands(self) -> list[Command]: ...

    @abstractmethod
    def handle_command(self, engine: GameEngine, action: str) -> ActionResult | None: ...

class ExploringState(PhaseState):
    phase = Phase.EXPLORING
    available_commands = [Command.EXPLORE, Command.INVENTORY]

    def handle_command(self, engine, action):
        if action == "explore":
            return engine.enter_new_room()
        if action == "inventory":
            return self._show_inventory(engine)
        return None

class CombatState(PhaseState):
    phase = Phase.COMBAT
    available_commands = [Command.ATTACK, Command.FLEE, Command.USE_ITEM]
    ...

class ShopState(PhaseState):
    phase = Phase.SHOP
    available_commands = [Command.BROWSE, Command.LEAVE]
    ...
```

Registry mapping `Phase` → `PhaseState`:

```python
PHASE_STATES: dict[Phase, PhaseState] = {
    Phase.EXPLORING: ExploringState(),
    Phase.COMBAT: CombatState(),
    Phase.SHOP: ShopState(),
}
```

### Impact

- `GameScreen._update_commands` and `_handle_command` collapse to looking up the current `PhaseState` and delegating.
- Engine stays a collection of action methods; phase states own **which actions are valid when**.
- Adding a new phase means: create a new `PhaseState` subclass, add it to `PHASE_STATES`.
- Phase states are pure functions of `(state, action)` — trivially testable without Textual.

### Files changed

- `game/phase_states.py` — **new file** with `PhaseState` ABC + implementations + registry
- `tui/screens.py` — replace `_update_commands` and `_handle_command` with `PhaseState` delegation
- `game/engine.py` — remove any phase-dispatch logic that moves to states

---

## Sequence of Implementation

The three changes are independent enough to be implemented in any order, but this sequence minimizes risk:

1. **Enums** — simplest, no behavioral changes, just type safety
2. **Item Strategy** — moderate refactor, behavioral change localized to items
3. **Phase States** — most structural, but by this point the codebase is cleaner

Each change leaves the project in a working, tested state.

## What's NOT Changing

- `ActionResult`, `GameState`, `Player`, `Monster`, `CombatState` models
- `dice.py` random mechanics
- `tui/widgets.py`, `tui/app.py`
- The overall `game/` vs `tui/` separation of concerns
- `docs/DARK_FORT.md` (canonical game design document)

## Success Criteria

- `make test` passes after each change
- `make lint` passes after each change
- Adding a new item type requires changes to **only** `game/models.py` (the new subclass)
- Adding a new room event requires changes to **only** `game/enums.py` (enum member) and `game/rules.py` (handler)
- Adding a new phase requires changes to **only** `game/phase_states.py` (new state class) and `game/enums.py` (enum member)
