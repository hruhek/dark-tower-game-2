# Design Patterns for Maintainability — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply Enum, Strategy, and State patterns to make adding new content (items, room events, phases) additive instead of scattered across files.

**Architecture:** Replace stringly-typed data with enums; give Item subclasses `use()` and `display_stats()` methods; extract PhaseState objects that own command availability and dispatch. Three sequential passes: Enums → Item Strategy → Phase States.

**Tech Stack:** Python 3.12, Pydantic, pytest, Textual, ruff, pyright

---

## File Map

| File | Responsibility |
|---|---|
| `src/dark_fort/game/enums.py` | All StrEnum definitions (ItemType, MonsterTier, Phase, Command, ScrollType, **RoomEvent**, **MonsterSpecial**) |
| `src/dark_fort/game/models.py` | Pydantic models; **Item subclasses gain `use()` and `display_stats()`** |
| `src/dark_fort/game/tables.py` | Static data tables; **ROOM_RESULTS becomes `list[RoomEvent]`**; **Monster.special becomes `MonsterSpecial \| None`** |
| `src/dark_fort/game/rules.py` | Game rule implementations; **dispatch on enum members** |
| `src/dark_fort/game/engine.py` | GameEngine; **simplifies `use_item`, `buy_item`**; keeps action methods |
| `src/dark_fort/game/phase_states.py` | **NEW** — `PhaseState` ABC + `ExploringState`, `CombatState`, `ShopState` + registry |
| `src/dark_fort/tui/screens.py` | TUI screens; **delegates command availability and dispatch to PhaseState**; **removes isinstance chains** |
| `src/dark_fort/tui/widgets.py` | TUI widgets; **unchanged** |
| `src/dark_fort/tui/app.py` | TUI app; **unchanged** |
| `tests/game/test_rules.py` | Tests for rules; **add enum dispatch tests** |
| `tests/game/test_engine.py` | Tests for engine; **add item strategy tests** |
| `tests/game/test_phase_states.py` | **NEW** — tests for phase state objects |

---

## Task 1: Add RoomEvent enum

**Files:**
- Modify: `src/dark_fort/game/enums.py`

- [ ] **Step 1: Add `RoomEvent` StrEnum**

```python
class RoomEvent(StrEnum):
    EMPTY = "Nothing. Explored."
    PIT_TRAP = "Pit trap"
    SOOTHSAYER = "Riddling Soothsayer"
    WEAK_MONSTER = "Weak monster"
    TOUGH_MONSTER = "Tough monster"
    SHOP = "Void Peddler"
```

Add this enum after `ScrollType` in `enums.py`.

- [ ] **Step 2: Commit**

```bash
git add src/dark_fort/game/enums.py
git commit -m "feat(enums): add RoomEvent StrEnum"
```

---

## Task 2: Convert ROOM_RESULTS to list[RoomEvent]

**Files:**
- Modify: `src/dark_fort/game/tables.py`
- Modify: `src/dark_fort/game/rules.py`

- [ ] **Step 1: Update tables.py ROOM_RESULTS type**

Change:
```python
ROOM_RESULTS: list[str] = [
    "Nothing. Explored.",
    "Pit trap",
    "Riddling Soothsayer",
    "Weak monster",
    "Tough monster",
    "Void Peddler",
]
```

To:
```python
from dark_fort.game.enums import RoomEvent

ROOM_RESULTS: list[RoomEvent] = [
    RoomEvent.EMPTY,
    RoomEvent.PIT_TRAP,
    RoomEvent.SOOTHSAYER,
    RoomEvent.WEAK_MONSTER,
    RoomEvent.TOUGH_MONSTER,
    RoomEvent.SHOP,
]
```

- [ ] **Step 2: Update rules.py resolve_room_event signature**

Change:
```python
def resolve_room_event(
    state: GameState, room_result: str, dice_roll: int | None = None
) -> ActionResult:
```

To:
```python
def resolve_room_event(
    state: GameState, room_result: RoomEvent, dice_roll: int | None = None
) -> ActionResult:
```

- [ ] **Step 3: Update all string comparisons in resolve_room_event to enum members**

Change each `if room_result == "Pit trap":` etc. to `if room_result == RoomEvent.PIT_TRAP:` etc.

- [ ] **Step 4: Update enter_new_room in engine.py**

In `engine.py`, change:
```python
room_result_idx = roll("d6") - 1
room_result = ROOM_RESULTS[room_result_idx]
```

No code change needed here — the type is now `RoomEvent` and `ROOM_RESULTS` is `list[RoomEvent]`, so `room_result` is already typed correctly.

- [ ] **Step 5: Run tests**

Run: `make test`
Expected: All tests pass (behavioral change: none; type change only)

- [ ] **Step 6: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 7: Commit**

```bash
git add src/dark_fort/game/tables.py src/dark_fort/game/rules.py
git commit -m "refactor: convert ROOM_RESULTS to RoomEvent enum"
```

---

## Task 3: Add MonsterSpecial enum

**Files:**
- Modify: `src/dark_fort/game/enums.py`
- Modify: `src/dark_fort/game/tables.py`
- Modify: `src/dark_fort/game/rules.py`
- Modify: `tests/game/test_rules.py`

- [ ] **Step 1: Add MonsterSpecial StrEnum to enums.py**

```python
class MonsterSpecial(StrEnum):
    LOOT_DAGGER = "loot_dagger_2_in_6"
    LOOT_SCROLL = "loot_scroll_2_in_6"
    LOOT_ROPE = "loot_rope_2_in_6"
    DEATH_RAY = "death_ray_1_in_6"
    PETRIFY = "petrify_1_in_6"
    INSTANT_LEVEL_UP = "instant_level_up_2_in_6"
    SEVEN_POINTS_ON_KILL = "7_points_on_kill"
```

- [ ] **Step 2: Update Monster model in tables.py**

Change:
```python
special: str | None = None
```

To:
```python
special: MonsterSpecial | None = None
```

- [ ] **Step 3: Update all Monster definitions in tables.py**

Change each `special="death_ray_1_in_6"` etc. to `special=MonsterSpecial.DEATH_RAY` etc.

Example for Necro-Sorcerer:
```python
Monster(
    name="Necro-Sorcerer",
    tier=MonsterTier.TOUGH,
    points=4,
    damage="d4",
    hp=8,
    loot="3d6 silver",
    special=MonsterSpecial.DEATH_RAY,
),
```

Do this for all monsters with special abilities.

- [ ] **Step 4: Update rules.py to dispatch on MonsterSpecial**

In `_resolve_loot`, change string comparisons to enum comparisons:
```python
if monster.special == MonsterSpecial.LOOT_DAGGER and chance_in_6(2):
    ...
elif monster.special == MonsterSpecial.LOOT_SCROLL and chance_in_6(2):
    ...
elif monster.special == MonsterSpecial.LOOT_ROPE and chance_in_6(2):
    ...
```

In `resolve_monster_special`, change string comparisons:
```python
if monster.special == MonsterSpecial.DEATH_RAY and special_roll == 1:
    return "The Necro-Sorcerer's death ray strikes! ..."
if monster.special == MonsterSpecial.PETRIFY and special_roll == 1:
    return "Medusa's gaze petrifies you! ..."
if monster.special == MonsterSpecial.INSTANT_LEVEL_UP and special_roll <= 2:
    return "The Basilisk's power surges through you! ..."
```

In `resolve_combat_hit`, change the special check:
```python
if monster.special == MonsterSpecial.SEVEN_POINTS_ON_KILL:
    messages.append("The troll crumbles to dust — 7 points earned!")
    player.points = max(0, player.points - monster.points) + 7
```

- [ ] **Step 5: Run tests**

Run: `make test`
Expected: All tests pass (behavioral change: none)

- [ ] **Step 6: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 7: Commit**

```bash
git add src/dark_fort/game/enums.py src/dark_fort/game/tables.py src/dark_fort/game/rules.py
git commit -m "refactor: convert monster specials to MonsterSpecial enum"
```

---

## Task 4: Add use() and display_stats() to Item subclasses

**Files:**
- Modify: `src/dark_fort/game/models.py`

- [ ] **Step 1: Update Item base class**

```python
class Item(BaseModel):
    name: str

    def use(self, state: GameState, index: int) -> ActionResult:
        raise NotImplementedError(f"use() not implemented for {type(self).__name__}")

    def display_stats(self) -> str:
        return ""
```

Note: `GameState` import may be needed — add `from dark_fort.game.models import GameState`... wait, that creates a circular import since GameState is defined later in the same file. Use `from __future__ import annotations` (already present) and a string annotation for the type hint, or import at the bottom. Actually, with `from __future__ import annotations`, forward references work in type hints. But `GameState` is used in the method body, not just the type hint.

Actually, looking at the current models.py, it already imports from `enums` and uses `from __future__ import annotations`. The `use()` method body references `GameState` which is defined later. We have two options:
1. Move `use()` to a separate module (but the skill pattern says behavior on the subclass)
2. Use a delayed import inside the method

Wait, actually `GameState` is defined in the same file. Since `from __future__ import annotations` is present, type hints can forward reference. But the method body needs the actual class. Since it's in the same file, we can just reference it once it's defined. But Python executes top-to-bottom, so `Item` is defined before `GameState`.

Solution: The `use()` methods will need to import `GameState` at runtime. Since `use()` is called after all models are defined, a local import inside each method body works. But that's ugly.

Alternative: Define `use()` as abstract in a protocol, and implement in a separate module. But the user already rejected the Protocol approach.

Alternative: Move `use()` implementations to a separate module (`game/item_actions.py`) that imports both `models` and `engine`. The Item base class still declares the method signature, but implementations live elsewhere.

Actually, looking more carefully: the Item subclasses need access to `GameState.player`, `GameState.combat`, etc. We can pass `GameState` as the parameter. Since the method is called after the module is fully loaded, we can use `TYPE_CHECKING` import or just import at module level after all classes are defined.

Actually, the cleanest approach for Pydantic models in the same file: since `from __future__ import annotations` is present, the type annotation `GameState` in the method signature will be a string (forward reference). For the method body, we can do:
```python
def use(self, state: "GameState", index: int) -> ActionResult:
    from dark_fort.game.models import GameState  # no-op at runtime but ensures typing
    # ... use state.player etc.
```

No, that's ugly. A better approach: since this is a Pydantic model file, keep it data-only and put behavior in a separate module. But the user explicitly wants behavior on the subclasses.

Let me re-read the user's response... They said "Base class methods (Recommended)". So they want the methods on the Pydantic subclasses.

Given the circular import issue (Item is defined before GameState), the best approach is:
1. Use `from __future__ import annotations` for type hints (already present)
2. In method bodies, just use `state` as-is — at runtime, `GameState` will be defined by the time `use()` is called
3. For pyright/mypy, this works fine because of forward references

Actually wait — at runtime, when `Item.use()` is CALLED (not when it's defined), `GameState` already exists. So there's no runtime issue. The only issue is if we tried to reference `GameState` at class definition time (e.g., as a default value). Since we're only using it in type hints and method bodies that execute later, it's fine.

Let me verify this... In Python with `from __future__ import annotations`, all annotations are stored as strings. So `state: GameState` becomes `state: 'GameState'` internally. At runtime, the method body just accesses `state.player` etc., which works because `state` is an instance of whatever is passed in. So this is fine.

- [ ] **Step 2: Add display_stats() to Weapon**

```python
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
        messages: list[str] = []
        player = state.player
        if player.weapon is not None:
            player.inventory.append(player.weapon)
            messages.append(f"{player.weapon.name} moved to inventory.")
        player.weapon = self
        messages.append(f"You equip the {self.name}.")
        player.inventory.pop(index)
        return ActionResult(messages=messages)
```

- [ ] **Step 3: Add display_stats() and use() to Armor**

```python
class Armor(Item):
    type: Literal[ItemType.ARMOR] = ItemType.ARMOR
    absorb: str = "d4"

    def display_stats(self) -> str:
        return self.absorb

    def use(self, state: GameState, index: int) -> ActionResult:
        messages: list[str] = []
        player = state.player
        if player.armor is not None:
            player.inventory.append(player.armor)
            messages.append(f"{player.armor.name} moved to inventory.")
        player.armor = self
        messages.append(f"You equip the {self.name}.")
        player.inventory.pop(index)
        return ActionResult(messages=messages)
```

- [ ] **Step 4: Add display_stats() and use() to Potion**

```python
class Potion(Item):
    type: Literal[ItemType.POTION] = ItemType.POTION
    heal: str

    def display_stats(self) -> str:
        return f"heal {self.heal}"

    def use(self, state: GameState, index: int) -> ActionResult:
        from dark_fort.game.dice import roll
        messages: list[str] = []
        player = state.player
        heal = roll(self.heal)
        player.hp = min(player.hp + heal, player.max_hp)
        messages.append(f"You drink the potion and heal {heal} HP.")
        player.inventory.pop(index)
        return ActionResult(messages=messages)
```

- [ ] **Step 5: Add display_stats() and use() to Scroll**

```python
class Scroll(Item):
    type: Literal[ItemType.SCROLL] = ItemType.SCROLL
    scroll_type: ScrollType

    def display_stats(self) -> str:
        return ""

    def use(self, state: GameState, index: int) -> ActionResult:
        messages = [f"You unroll the {self.name}..."]
        state.player.inventory.pop(index)
        return ActionResult(messages=messages)
```

- [ ] **Step 6: Add display_stats() and use() to Rope**

```python
class Rope(Item):
    type: Literal[ItemType.ROPE] = ItemType.ROPE

    def display_stats(self) -> str:
        return ""

    def use(self, state: GameState, index: int) -> ActionResult:
        return ActionResult(messages=["You can't use rope directly."])
```

- [ ] **Step 7: Add display_stats() and use() to Cloak**

```python
class Cloak(Item):
    type: Literal[ItemType.CLOAK] = ItemType.CLOAK

    def display_stats(self) -> str:
        return ""

    def use(self, state: GameState, index: int) -> ActionResult:
        player = state.player
        player.cloak_charges = max(0, player.cloak_charges - 1)
        return ActionResult(
            messages=[
                f"Cloak activated. {player.cloak_charges} charges remaining."
            ]
        )
```

- [ ] **Step 8: Run tests**

Run: `make test`
Expected: Tests pass. The new methods are unused by existing code yet, so no behavioral changes.

- [ ] **Step 9: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 10: Commit**

```bash
git add src/dark_fort/game/models.py
git commit -m "feat(models): add use() and display_stats() to Item subclasses"
```

---

## Task 5: Simplify engine.use_item() to delegate to items

**Files:**
- Modify: `src/dark_fort/game/engine.py`
- Modify: `tests/game/test_engine.py`

- [ ] **Step 1: Replace use_item implementation**

Replace the entire `use_item` method (lines 184-233):

```python
    def use_item(self, index: int) -> ActionResult:
        """Use an item from inventory."""
        if index < 0 or index >= len(self.state.player.inventory):
            return ActionResult(messages=["Invalid item index."])

        item = self.state.player.inventory[index]
        return item.use(self.state, index)
```

- [ ] **Step 2: Run tests**

Run: `make test`
Expected: Tests pass (behavioral change: delegated to item.use(), which has identical logic)

- [ ] **Step 3: Commit**

```bash
git add src/dark_fort/game/engine.py
git commit -m "refactor(engine): delegate use_item to item.use()"
```

---

## Task 6: Simplify TUI display to use item.display_stats()

**Files:**
- Modify: `src/dark_fort/tui/screens.py`

- [ ] **Step 1: Replace _show_inventory isinstance chain**

Replace the entire `_show_inventory` method with:

```python
    def _show_inventory(self) -> ActionResult:
        player = self.engine.state.player
        if not player.inventory:
            return ActionResult(messages=["Your inventory is empty."])

        messages = ["Inventory:"]
        type_prefixes = {
            ItemType.WEAPON: "W",
            ItemType.ARMOR: "A",
            ItemType.POTION: "P",
            ItemType.SCROLL: "S",
            ItemType.ROPE: "R",
            ItemType.CLOAK: "C",
        }
        for i, item in enumerate(player.inventory):
            prefix = type_prefixes.get(item.type, "?")
            stats = item.display_stats()
            stats_str = f" ({stats})" if stats else ""
            messages.append(f"  {i + 1}. [{prefix}] {item.name}{stats_str}")
        return ActionResult(messages=messages)
```

- [ ] **Step 2: Replace ShopScreen.on_mount isinstance chain**

Replace the shop item display loop in `ShopScreen.on_mount`:

```python
        log = self.query_one("#shop-log", LogView)
        log.add_message("Available wares:")
        for i, (item, price) in enumerate(SHOP_ITEMS):
            stats = item.display_stats()
            stats_str = f" ({stats})" if stats else ""
            log.add_message(f"  {i + 1}. {item.name}{stats_str} — {price}s")
        log.add_message(f"\nYour silver: {self.engine.state.player.silver}s")
        log.add_message("Press 1-9, 0 for item 10, or L to leave.")
        self.focus()
```

- [ ] **Step 3: Update imports in screens.py**

Remove the individual item type imports (`Armor`, `Cloak`, `Potion`, `Rope`, `Scroll`, `Weapon`) if they are no longer used directly. Add `ItemType` import from `enums` if not already present.

- [ ] **Step 4: Run tests**

Run: `make test`
Expected: Tests pass (display output should be identical)

- [ ] **Step 5: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 6: Commit**

```bash
git add src/dark_fort/tui/screens.py
git commit -m "refactor(tui): use item.display_stats() instead of isinstance chains"
```

---

## Task 7: Create PhaseState ABC and implementations

**Files:**
- Create: `src/dark_fort/game/phase_states.py`
- Modify: `tests/game/test_phase_states.py` (new test file)

- [ ] **Step 1: Create phase_states.py with PhaseState ABC**

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from dark_fort.game.enums import Command, Phase
from dark_fort.game.models import ActionResult


class PhaseState(ABC):
    @property
    @abstractmethod
    def phase(self) -> Phase: ...

    @property
    @abstractmethod
    def available_commands(self) -> list[Command]: ...

    @abstractmethod
    def handle_command(
        self, engine: "dark_fort.game.engine.GameEngine", action: str
    ) -> ActionResult | None: ...
```

- [ ] **Step 2: Add ExploringState**

```python
class ExploringState(PhaseState):
    phase = Phase.EXPLORING
    available_commands = [Command.EXPLORE, Command.INVENTORY]

    def handle_command(self, engine, action):
        if action == "explore":
            return engine.enter_new_room()
        if action == "inventory":
            from dark_fort.game.engine import GameEngine

            player = engine.state.player
            if not player.inventory:
                return ActionResult(messages=["Your inventory is empty."])
            messages = ["Inventory:"]
            type_prefixes = {
                "weapon": "W",
                "armor": "A",
                "potion": "P",
                "scroll": "S",
                "rope": "R",
                "cloak": "C",
            }
            for i, item in enumerate(player.inventory):
                prefix = type_prefixes.get(item.type, "?")
                stats = item.display_stats()
                stats_str = f" ({stats})" if stats else ""
                messages.append(f"  {i + 1}. [{prefix}] {item.name}{stats_str}")
            return ActionResult(messages=messages)
        return None
```

- [ ] **Step 3: Add CombatState**

```python
class CombatState(PhaseState):
    phase = Phase.COMBAT
    available_commands = [Command.ATTACK, Command.FLEE, Command.USE_ITEM]

    def handle_command(self, engine, action):
        if action == "attack":
            return engine.attack()
        if action == "flee":
            return engine.flee()
        if action == "use_item":
            return ActionResult(messages=["Use item: (type item number)"])
        return None
```

- [ ] **Step 4: Add ShopState**

```python
class ShopState(PhaseState):
    phase = Phase.SHOP
    available_commands = [Command.BROWSE, Command.LEAVE]

    def handle_command(self, engine, action):
        if action == "leave":
            return engine.leave_shop()
        if action == "browse":
            from dark_fort.game.tables import SHOP_ITEMS

            messages = ["Available wares:"]
            for i, (item, price) in enumerate(SHOP_ITEMS):
                stats = item.display_stats()
                stats_str = f" ({stats})" if stats else ""
                messages.append(f"  {i + 1}. {item.name}{stats_str} — {price}s")
            messages.append(f"\nYour silver: {engine.state.player.silver}s")
            messages.append("Press 1-9, 0 for item 10, or L to leave.")
            return ActionResult(messages=messages)
        return None
```

- [ ] **Step 5: Add registry**

```python
PHASE_STATES: dict[Phase, PhaseState] = {
    Phase.EXPLORING: ExploringState(),
    Phase.COMBAT: CombatState(),
    Phase.SHOP: ShopState(),
}
```

- [ ] **Step 6: Run tests**

Run: `make test`
Expected: Pass (new file, not yet wired up)

- [ ] **Step 7: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 8: Commit**

```bash
git add src/dark_fort/game/phase_states.py
git commit -m "feat(phase_states): add PhaseState ABC and implementations"
```

---

## Task 8: Wire PhaseState into GameScreen

**Files:**
- Modify: `src/dark_fort/tui/screens.py`
- Modify: `tests/tui/test_screens.py`

- [ ] **Step 1: Import PHASE_STATES in screens.py**

```python
from dark_fort.game.phase_states import PHASE_STATES
```

- [ ] **Step 2: Replace _update_commands with PhaseState delegation**

```python
    def _update_commands(self) -> None:
        phase = self.engine.state.phase
        state = PHASE_STATES.get(phase)
        commands = state.available_commands if state else []

        cmd_bar = self.query_one("#commands", CommandBar)
        cmd_bar.commands = commands

        status_bar = self.query_one(StatusBar)
        status_bar.player = self.engine.state.player
        status_bar.explored = self.engine.explored_count
```

- [ ] **Step 3: Replace _handle_command with PhaseState delegation**

```python
    def _handle_command(self, action: str) -> ActionResult | None:
        phase = self.engine.state.phase
        state = PHASE_STATES.get(phase)
        if state:
            return state.handle_command(self.engine, action)
        return None
```

- [ ] **Step 4: Remove old command handlers from GameScreen**

Remove `_show_inventory` and `_show_use_item` methods from `GameScreen` (their logic is now in `ExploringState` and `CombatState`).

- [ ] **Step 5: Update on_button_pressed in GameScreen**

```python
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if not button_id.startswith("cmd-"):
            return

        action = button_id.replace("cmd-", "")
        result = self._handle_command(action)
        if result:
            self._log_messages(result.messages)
            if result.phase:
                self._handle_phase_change(result)
            self._update_commands()
```

- [ ] **Step 6: Run tests**

Run: `make test`
Expected: Tests pass. GameScreen now delegates to PhaseState objects.

- [ ] **Step 7: Run lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 8: Commit**

```bash
git add src/dark_fort/tui/screens.py
git commit -m "refactor(tui): delegate command availability and dispatch to PhaseState"
```

---

## Task 9: Add tests for PhaseState objects

**Files:**
- Create: `tests/game/test_phase_states.py`

- [ ] **Step 1: Write test for ExploringState**

```python
import pytest
from dark_fort.game.engine import GameEngine
from dark_fort.game.enums import Command, Phase
from dark_fort.game.phase_states import ExploringState, PHASE_STATES


def test_exploring_state_phase():
    state = ExploringState()
    assert state.phase == Phase.EXPLORING


def test_exploring_state_commands():
    state = ExploringState()
    assert Command.EXPLORE in state.available_commands
    assert Command.INVENTORY in state.available_commands


def test_exploring_state_handle_explore():
    engine = GameEngine()
    engine.start_game()
    state = PHASE_STATES[Phase.EXPLORING]
    result = state.handle_command(engine, "explore")
    assert result is not None
    assert len(result.messages) > 0


def test_exploring_state_handle_inventory():
    engine = GameEngine()
    engine.start_game()
    state = PHASE_STATES[Phase.EXPLORING]
    result = state.handle_command(engine, "inventory")
    assert result is not None
    assert "Inventory:" in result.messages
```

- [ ] **Step 2: Write test for CombatState**

```python
from dark_fort.game.phase_states import CombatState


def test_combat_state_phase():
    state = CombatState()
    assert state.phase == Phase.COMBAT


def test_combat_state_commands():
    state = CombatState()
    assert Command.ATTACK in state.available_commands
    assert Command.FLEE in state.available_commands
    assert Command.USE_ITEM in state.available_commands
```

- [ ] **Step 3: Write test for ShopState**

```python
from dark_fort.game.phase_states import ShopState


def test_shop_state_phase():
    state = ShopState()
    assert state.phase == Phase.SHOP


def test_shop_state_commands():
    state = ShopState()
    assert Command.BROWSE in state.available_commands
    assert Command.LEAVE in state.available_commands
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/game/test_phase_states.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add tests/game/test_phase_states.py
git commit -m "test(phase_states): add tests for PhaseState objects"
```

---

## Task 10: Final verification

**Files:** All

- [ ] **Step 1: Run full test suite**

Run: `make test`
Expected: All tests pass

- [ ] **Step 2: Run full lint**

Run: `make lint`
Expected: Pass

- [ ] **Step 3: Final commit**

```bash
git status  # verify no uncommitted changes
git log --oneline -5  # review commit history
```

---

## Self-Review

### Spec coverage check

| Spec Section | Implementing Task |
|---|---|
| RoomEvent enum | Task 1 |
| ROOM_RESULTS as list[RoomEvent] | Task 2 |
| MonsterSpecial enum | Task 3 |
| Monster.special as MonsterSpecial \| None | Task 3 |
| Item.use() and display_stats() | Task 4 |
| engine.use_item delegates to item.use() | Task 5 |
| TUI removes isinstance chains | Task 6 |
| PhaseState ABC | Task 7 |
| ExploringState, CombatState, ShopState | Task 7 |
| PHASE_STATES registry | Task 7 |
| GameScreen delegates to PhaseState | Task 8 |
| Tests for phase states | Task 9 |

No gaps found.

### Placeholder scan

- No "TBD", "TODO", "implement later", "fill in details"
- No vague "add error handling" steps
- No "similar to Task N" references
- All code steps contain actual code
- All test steps contain actual test code

### Type consistency check

- `RoomEvent` used consistently across tables, rules, engine
- `MonsterSpecial` used consistently across tables, rules
- `PhaseState.handle_command` signature matches in ABC and all subclasses
- `Item.use(state: GameState, index: int) -> ActionResult` signature consistent
- `Item.display_stats() -> str` signature consistent

No type inconsistencies found.

Plan complete and ready for execution.
