# Inventory & Equip System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow the player to carry multiple weapons and armor in inventory, equip one of each, and swap equipped items back to inventory when equipping a replacement.

**Architecture:** Add an `Armor` model (mirroring `Weapon`), change `Player.armor` from `bool` to `Armor | None`, add `Item.absorb` field, add conversion helpers, update equip logic to swap instead of consume, fix `weapon.attack_bonus` in combat, and update TUI to display armor stats.

**Tech Stack:** Python 3.12+, Pydantic, Textual, pytest

---

### Task 1: Add Armor model and Item.absorb field

**Files:**
- Modify: `src/dark_fort/game/models.py`
- Test: `tests/game/test_models.py`

- [ ] **Step 1: Write failing tests for Armor model and Item.absorb**

Add to `tests/game/test_models.py`:

```python
from dark_fort.game.models import Armor

class TestArmor:
    def test_create_armor(self):
        armor = Armor(name="Armor", absorb="d4")
        assert armor.name == "Armor"
        assert armor.absorb == "d4"

    def test_armor_default_absorb(self):
        armor = Armor(name="Armor")
        assert armor.absorb == "d4"

class TestItemAbsorb:
    def test_create_armor_item_with_absorb(self):
        item = Item(name="Armor", type=ItemType.ARMOR, absorb="d4")
        assert item.absorb == "d4"

    def test_item_absorb_defaults_none(self):
        item = Item(name="Potion", type=ItemType.POTION)
        assert item.absorb is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_models.py::TestArmor tests/game/test_models.py::TestItemAbsorb -v`
Expected: FAIL (ImportError for Armor, absorb not on Item)

- [ ] **Step 3: Add Armor model and Item.absorb field**

In `src/dark_fort/game/models.py`, add `Armor` class after `Weapon`:

```python
class Armor(BaseModel):
    name: str
    absorb: str = "d4"
```

Add `absorb` field to `Item`:

```python
class Item(BaseModel):
    name: str
    type: ItemType
    damage: str | None = None
    attack_bonus: int = 0
    absorb: str | None = None
    uses: int | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_models.py::TestArmor tests/game/test_models.py::TestItemAbsorb -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/models.py tests/game/test_models.py
git commit -m "feat: add Armor model and Item.absorb field"
```

---

### Task 2: Change Player.armor from bool to Armor | None

**Files:**
- Modify: `src/dark_fort/game/models.py`
- Test: `tests/game/test_models.py`

- [ ] **Step 1: Write failing test for Player.armor as Armor | None**

Add to `tests/game/test_models.py`:

```python
class TestPlayerArmor:
    def test_player_armor_defaults_none(self):
        player = Player()
        assert player.armor is None

    def test_player_can_equip_armor(self):
        player = Player()
        player.armor = Armor(name="Armor", absorb="d4")
        assert player.armor is not None
        assert player.armor.name == "Armor"
        assert player.armor.absorb == "d4"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_models.py::TestPlayerArmor -v`
Expected: FAIL (Player.armor is currently `bool`, not `Armor | None`)

- [ ] **Step 3: Change Player.armor field type**

In `src/dark_fort/game/models.py`, change `Player.armor`:

```python
class Player(BaseModel):
    name: str = "Kargunt"
    hp: int = 15
    max_hp: int = 15
    silver: int = 0
    points: int = 0
    weapon: Weapon | None = None
    armor: Armor | None = None
    inventory: list[Item] = []
    scrolls: list[Item] = []
    cloak_charges: int = 0
    attack_bonus: int = 0
    level_benefits: list[int] = []
    daemon_fights_remaining: int = 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_models.py::TestPlayerArmor -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/models.py tests/game/test_models.py
git commit -m "feat: change Player.armor from bool to Armor | None"
```

---

### Task 3: Add conversion helpers (weapon_to_item, armor_to_item)

**Files:**
- Modify: `src/dark_fort/game/models.py`
- Test: `tests/game/test_models.py`

- [ ] **Step 1: Write failing tests for conversion helpers**

Add to `tests/game/test_models.py`:

```python
from dark_fort.game.models import armor_to_item, weapon_to_item

class TestConversionHelpers:
    def test_weapon_to_item(self):
        weapon = Weapon(name="Sword", damage="d6", attack_bonus=1)
        item = weapon_to_item(weapon)
        assert item.name == "Sword"
        assert item.type == ItemType.WEAPON
        assert item.damage == "d6"
        assert item.attack_bonus == 1

    def test_armor_to_item(self):
        armor = Armor(name="Armor", absorb="d4")
        item = armor_to_item(armor)
        assert item.name == "Armor"
        assert item.type == ItemType.ARMOR
        assert item.absorb == "d4"

    def test_weapon_to_item_preserves_all_fields(self):
        weapon = Weapon(name="Flail", damage="d6+1")
        item = weapon_to_item(weapon)
        assert item.attack_bonus == 0
        assert item.damage == "d6+1"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_models.py::TestConversionHelpers -v`
Expected: FAIL (ImportError for conversion helpers)

- [ ] **Step 3: Add conversion helpers to models.py**

In `src/dark_fort/game/models.py`, add after the `Player` class:

```python
def weapon_to_item(weapon: Weapon) -> Item:
    return Item(
        name=weapon.name,
        type=ItemType.WEAPON,
        damage=weapon.damage,
        attack_bonus=weapon.attack_bonus,
    )


def armor_to_item(armor: Armor) -> Item:
    return Item(
        name=armor.name,
        type=ItemType.ARMOR,
        absorb=armor.absorb,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_models.py::TestConversionHelpers -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/models.py tests/game/test_models.py
git commit -m "feat: add weapon_to_item and armor_to_item conversion helpers"
```

---

### Task 4: Update tables.py — ARMOR_TABLE and SHOP_ITEMS

**Files:**
- Modify: `src/dark_fort/game/tables.py`
- Test: `tests/game/test_tables.py`

- [ ] **Step 1: Write failing test for ARMOR_TABLE and updated SHOP_ITEMS**

Add to `tests/game/test_tables.py`:

```python
from dark_fort.game.models import Armor, Item
from dark_fort.game.enums import ItemType
from dark_fort.game.tables import ARMOR_TABLE, SHOP_ITEMS

class TestArmorTable:
    def test_armor_table_has_entries(self):
        assert len(ARMOR_TABLE) >= 1

    def test_armor_table_first_entry(self):
        armor = ARMOR_TABLE[0]
        assert armor.name == "Armor"
        assert armor.absorb == "d4"

class TestShopItemsArmor:
    def test_armor_shop_item_has_absorb(self):
        armor_items = [(item, price) for item, price in SHOP_ITEMS if item.type == ItemType.ARMOR]
        assert len(armor_items) >= 1
        armor_item, price = armor_items[0]
        assert armor_item.absorb == "d4"
        assert price == 10
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_tables.py::TestArmorTable tests/game/test_tables.py::TestShopItemsArmor -v`
Expected: FAIL (ARMOR_TABLE doesn't exist, armor Item has no absorb)

- [ ] **Step 3: Add ARMOR_TABLE and update SHOP_ITEMS**

In `src/dark_fort/game/tables.py`:

1. Add import for `Armor`:
```python
from dark_fort.game.models import Armor, Item, Monster, Weapon
```

2. Add `ARMOR_TABLE` after `WEAPONS_TABLE`:
```python
ARMOR_TABLE: list[Armor] = [
    Armor(name="Armor", absorb="d4"),
]
```

3. Update the armor entry in `SHOP_ITEMS`:
```python
(Item(name="Armor", type=ItemType.ARMOR, absorb="d4"), 10),
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_tables.py::TestArmorTable tests/game/test_tables.py::TestShopItemsArmor -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/tables.py tests/game/test_tables.py
git commit -m "feat: add ARMOR_TABLE and update SHOP_ITEMS with absorb"
```

---

### Task 5: Update rules.py — fix weapon.attack_bonus and armor.absorb in combat

**Files:**
- Modify: `src/dark_fort/game/rules.py`
- Test: `tests/game/test_rules.py`

- [ ] **Step 1: Write failing tests for weapon attack_bonus and armor absorb**

Add to `tests/game/test_rules.py`:

```python
from dark_fort.game.models import Armor

class TestWeaponAttackBonus:
    def test_weapon_attack_bonus_adds_to_hit_roll(self):
        monster = Monster(
            name="Goblin", tier=MonsterTier.WEAK, points=3, damage="d4", hp=5
        )
        player = Player(weapon=Weapon(name="Dagger", damage="d4", attack_bonus=1))
        combat = CombatState(monster=monster, monster_hp=5)
        result = resolve_combat_hit(player, combat, player_roll=2)
        assert any("HIT" in m for m in result.messages)

    def test_weapon_attack_bonus_still_misses_low_roll(self):
        monster = Monster(
            name="Goblin", tier=MonsterTier.WEAK, points=5, damage="d4", hp=5
        )
        player = Player(weapon=Weapon(name="Dagger", damage="d4", attack_bonus=1))
        combat = CombatState(monster=monster, monster_hp=5)
        result = resolve_combat_hit(player, combat, player_roll=2)
        assert any("MISS" in m for m in result.messages)

class TestArmorAbsorb:
    def test_armor_absorbs_damage(self):
        monster = Monster(
            name="Goblin", tier=MonsterTier.WEAK, points=3, damage="d4", hp=5
        )
        player = Player(hp=15, armor=Armor(name="Armor", absorb="d4"))
        combat = CombatState(monster=monster, monster_hp=5)
        result = resolve_combat_hit(player, combat, player_roll=2)
        assert any("Armor absorbs" in m for m in result.messages)

    def test_no_armor_no_absorb_message(self):
        monster = Monster(
            name="Goblin", tier=MonsterTier.WEAK, points=3, damage="d4", hp=5
        )
        player = Player(hp=15)
        combat = CombatState(monster=monster, monster_hp=5)
        result = resolve_combat_hit(player, combat, player_roll=2)
        assert not any("Armor absorbs" in m for m in result.messages)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_rules.py::TestWeaponAttackBonus tests/game/test_rules.py::TestArmorAbsorb -v`
Expected: FAIL (weapon attack_bonus not applied, armor is now `Armor | None` not `bool`)

- [ ] **Step 3: Update resolve_combat_hit in rules.py**

In `src/dark_fort/game/rules.py`:

1. Add `Armor` to imports:
```python
from dark_fort.game.models import (
    ActionResult,
    Armor,
    CombatState,
    GameState,
    Item,
    Monster,
    Player,
    Weapon,
)
```

2. Change the effective_roll line (line 47) from:
```python
effective_roll = player_roll + player.attack_bonus
```
to:
```python
weapon_bonus = player.weapon.attack_bonus if player.weapon else 0
effective_roll = player_roll + player.attack_bonus + weapon_bonus
```

3. Change the hit roll message (line 54) from:
```python
f"Rolling to hit... you rolled {player_roll} (+{player.attack_bonus} bonus)"
```
to:
```python
total_bonus = player.attack_bonus + weapon_bonus
f"Rolling to hit... you rolled {player_roll} (+{total_bonus} bonus)"
```

4. Change the armor check (lines 86-89) from:
```python
if player.armor:
    absorbed = roll("d4")
    monster_dmg = max(0, monster_dmg - absorbed)
    messages.append(f"Armor absorbs {absorbed} damage")
```
to:
```python
if player.armor:
    absorbed = roll(player.armor.absorb)
    monster_dmg = max(0, monster_dmg - absorbed)
    messages.append(f"{player.armor.name} absorbs {absorbed} damage")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_rules.py::TestWeaponAttackBonus tests/game/test_rules.py::TestArmorAbsorb -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/rules.py tests/game/test_rules.py
git commit -m "feat: apply weapon attack_bonus in combat and use armor absorb"
```

---

### Task 6: Update rules.py — generate_starting_equipment for Armor model

**Files:**
- Modify: `src/dark_fort/game/rules.py`
- Test: `tests/game/test_rules.py`

- [ ] **Step 1: Write failing test for starting armor as Armor object**

Add to `tests/game/test_rules.py`:

```python
class TestStartingEquipmentArmor:
    def test_starting_armor_item_has_absorb(self):
        weapon, item = generate_starting_equipment()
        if item.type == ItemType.ARMOR:
            assert item.absorb == "d4"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/game/test_rules.py::TestStartingEquipmentArmor -v`
Expected: FAIL (armor Item doesn't have `absorb` field yet)

- [ ] **Step 3: Update generate_starting_equipment in rules.py**

In `src/dark_fort/game/rules.py`, change the armor entry in `item_table` from:
```python
Item(name="Armor", type=ItemType.ARMOR),
```
to:
```python
Item(name="Armor", type=ItemType.ARMOR, absorb="d4"),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/game/test_rules.py::TestStartingEquipmentArmor -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/rules.py tests/game/test_rules.py
git commit -m "feat: add absorb to starting armor item"
```

---

### Task 7: Update engine.py — equip/swap logic for weapons and armor

**Files:**
- Modify: `src/dark_fort/game/engine.py`
- Test: `tests/game/test_engine.py`

- [ ] **Step 1: Write failing tests for equip/swap logic**

Add to `tests/game/test_engine.py`:

```python
from dark_fort.game.models import Armor, Item, Weapon
from dark_fort.game.enums import ItemType

class TestEquipWeapon:
    def test_equip_weapon_from_inventory(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.inventory.append(
            Item(name="Sword", type=ItemType.WEAPON, damage="d6", attack_bonus=1)
        )
        result = engine.use_item(0)
        assert engine.state.player.weapon is not None
        assert engine.state.player.weapon.name == "Sword"
        assert len(engine.state.player.inventory) == 0 or all(
            item.name != "Sword" for item in engine.state.player.inventory
            if item.type == ItemType.WEAPON
        )

    def test_equip_weapon_swaps_old_to_inventory(self):
        engine = GameEngine()
        engine.start_game()
        old_weapon = engine.state.player.weapon
        assert old_weapon is not None
        engine.state.player.inventory.append(
            Item(name="Sword", type=ItemType.WEAPON, damage="d6", attack_bonus=1)
        )
        engine.use_item(0)
        assert engine.state.player.weapon.name == "Sword"
        assert any(item.name == old_weapon.name for item in engine.state.player.inventory)

    def test_equip_weapon_when_none_equipped(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.weapon = None
        engine.state.player.inventory.append(
            Item(name="Dagger", type=ItemType.WEAPON, damage="d4", attack_bonus=1)
        )
        engine.use_item(0)
        assert engine.state.player.weapon is not None
        assert engine.state.player.weapon.name == "Dagger"

class TestEquipArmor:
    def test_equip_armor_from_inventory(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.inventory.append(
            Item(name="Armor", type=ItemType.ARMOR, absorb="d4")
        )
        result = engine.use_item(0)
        assert engine.state.player.armor is not None
        assert engine.state.player.armor.name == "Armor"

    def test_equip_armor_swaps_old_to_inventory(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.armor = Armor(name="Old Armor", absorb="d4")
        engine.state.player.inventory.append(
            Item(name="New Armor", type=ItemType.ARMOR, absorb="d6")
        )
        engine.use_item(0)
        assert engine.state.player.armor.name == "New Armor"
        assert any(item.name == "Old Armor" for item in engine.state.player.inventory)

    def test_equip_armor_when_none_equipped(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.armor = None
        engine.state.player.inventory.append(
            Item(name="Armor", type=ItemType.ARMOR, absorb="d4")
        )
        engine.use_item(0)
        assert engine.state.player.armor is not None
        assert engine.state.player.armor.name == "Armor"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_engine.py::TestEquipWeapon tests/game/test_engine.py::TestEquipArmor -v`
Expected: FAIL (current use_item doesn't swap, armor equip doesn't create Armor object)

- [ ] **Step 3: Update use_item in engine.py**

In `src/dark_fort/game/engine.py`:

1. Add `Armor` and `armor_to_item`, `weapon_to_item` to imports:
```python
from dark_fort.game.models import ActionResult, Armor, GameState, Item, Room, Weapon
from dark_fort.game.models import armor_to_item, weapon_to_item
```

2. Replace the weapon equip block in `use_item()` (lines 187-194) with:
```python
elif item.type == "weapon":
    if self.state.player.weapon is not None:
        self.state.player.inventory.append(
            weapon_to_item(self.state.player.weapon)
        )
        messages.append(f"{self.state.player.weapon.name} moved to inventory.")
    self.state.player.weapon = Weapon(
        name=item.name,
        damage=item.damage or "d4",
        attack_bonus=item.attack_bonus,
    )
    messages.append(f"You equip the {item.name}.")
    self.state.player.inventory.pop(index)
```

3. Add armor equip block after the weapon block (before the cloak block):
```python
elif item.type == "armor":
    if self.state.player.armor is not None:
        self.state.player.inventory.append(
            armor_to_item(self.state.player.armor)
        )
        messages.append(f"{self.state.player.armor.name} moved to inventory.")
    self.state.player.armor = Armor(
        name=item.name,
        absorb=item.absorb or "d4",
    )
    messages.append(f"You equip the {item.name}.")
    self.state.player.inventory.pop(index)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_engine.py::TestEquipWeapon tests/game/test_engine.py::TestEquipArmor -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dark_fort/game/engine.py tests/game/test_engine.py
git commit -m "feat: add weapon and armor equip/swap logic in use_item"
```

---

### Task 8: Update engine.py — buy_item armor handling and start_game armor handling

**Files:**
- Modify: `src/dark_fort/game/engine.py`
- Test: `tests/game/test_engine.py`

- [ ] **Step 1: Write failing tests for buying armor and starting with armor**

Add to `tests/game/test_engine.py`:

```python
class TestBuyArmor:
    def test_buy_armor_equips_it(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.silver = 20
        engine.state.phase = Phase.SHOP
        result = engine.buy_item(8)  # Armor is index 8
        assert engine.state.player.armor is not None
        assert engine.state.player.armor.name == "Armor"
        assert engine.state.player.armor.absorb == "d4"

    def test_buy_armor_swaps_existing(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.armor = Armor(name="Old Armor", absorb="d4")
        engine.state.player.silver = 20
        engine.state.phase = Phase.SHOP
        result = engine.buy_item(8)  # Armor is index 8
        assert engine.state.player.armor.name == "Armor"
        assert any(item.name == "Old Armor" for item in engine.state.player.inventory)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/game/test_engine.py::TestBuyArmor -v`
Expected: FAIL (buy_item still sets `armor = True`)

- [ ] **Step 3: Update buy_item in engine.py**

In `src/dark_fort/game/engine.py`, replace the armor block in `buy_item()` (lines 140-142):

From:
```python
if item.type == "armor":
    self.state.player.armor = True
    msg = f"You buy {item.name} for {price}s."
```

To:
```python
if item.type == "armor":
    if self.state.player.armor is not None:
        self.state.player.inventory.append(
            armor_to_item(self.state.player.armor)
        )
        msg = f"You buy {item.name} for {price}s. {self.state.player.armor.name} moved to inventory."
    else:
        msg = f"You buy {item.name} for {price}s."
    self.state.player.armor = Armor(
        name=item.name,
        absorb=item.absorb or "d4",
    )
```

- [ ] **Step 4: Update start_game in engine.py**

In `src/dark_fort/game/engine.py`, change the armor handling in `start_game()` (lines 42-43):

From:
```python
if item.type == "armor":
    self.state.player.armor = True
```

To:
```python
if item.type == "armor":
    self.state.player.armor = Armor(name=item.name, absorb=item.absorb or "d4")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/game/test_engine.py::TestBuyArmor -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/dark_fort/game/engine.py tests/game/test_engine.py
git commit -m "feat: update buy_item and start_game for Armor model"
```

---

### Task 9: Update TUI — StatusBar armor display and inventory display

**Files:**
- Modify: `src/dark_fort/tui/widgets.py`
- Modify: `src/dark_fort/tui/screens.py`
- Test: `tests/tui/test_widgets.py`

- [ ] **Step 1: Write failing test for armor in StatusBar**

Add to `tests/tui/test_widgets.py`:

```python
from dark_fort.game.models import Armor

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
            assert "Armor" in str(armor_label.renderable)

    async def test_status_bar_shows_no_armor(self):
        player = Player(hp=15, max_hp=15, silver=18, points=5)
        player.weapon = Weapon(name="Sword", damage="d6")

        async with DarkFortApp().run_test() as pilot:
            bar = StatusBar(player=player, explored=3)
            pilot.app.screen.mount(bar)
            await pilot.pause()
            armor_label = bar.query_one("#armor", Label)
            assert "None" in str(armor_label.renderable)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tui/test_widgets.py::TestStatusBarArmor -v`
Expected: FAIL (no `#armor` label in StatusBar)

- [ ] **Step 3: Update StatusBar in widgets.py**

In `src/dark_fort/tui/widgets.py`:

1. Add `Armor` to imports:
```python
from dark_fort.game.models import Armor, Player
```

2. Add `#armor` label to `compose()`:
```python
def compose(self) -> ComposeResult:
    yield Label(id="hp")
    yield Label(id="silver")
    yield Label(id="points")
    yield Label(id="rooms")
    yield Label(id="weapon")
    yield Label(id="armor")
```

3. Add armor display to `_refresh()`, after the weapon block:
```python
armor_label = self.query_one("#armor", Label)
if self.player.armor:
    armor_label.update(
        f"Armor: {self.player.armor.name} ({self.player.armor.absorb})"
    )
else:
    armor_label.update("Armor: None")
```

- [ ] **Step 4: Update inventory display in screens.py**

In `src/dark_fort/tui/screens.py`, update `_show_inventory()`:

```python
def _show_inventory(self) -> ActionResult:
    player = self.engine.state.player
    if not player.inventory:
        return ActionResult(messages=["Your inventory is empty."])

    type_prefix = {
        "weapon": "W",
        "armor": "A",
        "potion": "P",
        "scroll": "S",
        "rope": "R",
        "cloak": "C",
    }
    messages = ["Inventory:"]
    for i, item in enumerate(player.inventory):
        prefix = type_prefix.get(item.type, "?")
        stats = ""
        if item.type == "weapon" and item.damage:
            stats = f" ({item.damage})"
        elif item.type == "armor" and item.absorb:
            stats = f" ({item.absorb})"
        elif item.type == "potion" and item.damage:
            stats = f" (heal {item.damage})"
        messages.append(f"  {i + 1}. [{prefix}] {item.name}{stats}")
    return ActionResult(messages=messages)
```

- [ ] **Step 5: Update shop display in screens.py**

In `src/dark_fort/tui/screens.py`, update `ShopScreen.on_mount()` to show item stats:

```python
def on_mount(self) -> None:
    from dark_fort.game.tables import SHOP_ITEMS

    log = self.query_one("#shop-log", LogView)
    log.add_message("Available wares:")
    for i, (item, price) in enumerate(SHOP_ITEMS):
        stats = ""
        if item.type == "weapon" and item.damage:
            stats = f" ({item.damage}"
            if item.attack_bonus:
                stats += f"/+{item.attack_bonus}"
            stats += ")"
        elif item.type == "armor" and item.absorb:
            stats = f" (-{item.absorb})"
        elif item.type == "potion" and item.damage:
            stats = f" (heal {item.damage})"
        log.add_message(f"  {i + 1}. {item.name}{stats} — {price}s")
    log.add_message(f"\nYour silver: {self.engine.state.player.silver}s")
    log.add_message("Press a number (1-10) to buy, or L to leave.")
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/tui/test_widgets.py::TestStatusBarArmor -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/dark_fort/tui/widgets.py src/dark_fort/tui/screens.py tests/tui/test_widgets.py
git commit -m "feat: add armor display to StatusBar and improve inventory/shop display"
```

---

### Task 10: Fix all existing tests for Player.armor change

**Files:**
- Modify: `tests/game/test_models.py`
- Modify: `tests/game/test_rules.py`
- Modify: `tests/game/test_engine.py`
- Modify: `tests/tui/test_widgets.py`
- Modify: `tests/tui/test_screens.py`

- [ ] **Step 1: Run full test suite to find all failures**

Run: `uv run pytest tests/ -v`
Expected: Some tests fail due to `Player.armor` changing from `bool` to `Armor | None`

- [ ] **Step 2: Fix test_models.py**

In `tests/game/test_models.py`, change `TestPlayer.test_default_player`:

From:
```python
assert player.armor is False
```

To:
```python
assert player.armor is None
```

- [ ] **Step 3: Fix any other test files referencing `armor=True` or `armor=False`**

Search all test files for `armor=True`, `armor=False`, `player.armor`, and `.armor` references. Update:
- `player.armor = True` → `player.armor = Armor(name="Armor", absorb="d4")`
- `player.armor = False` → `player.armor = None`
- `assert player.armor is False` → `assert player.armor is None`
- Any combat tests that set `armor=True` need `Armor` import and update

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "fix: update all tests for Player.armor Armor | None change"
```

---

### Task 11: Run lint and type checks

**Files:**
- All modified files

- [ ] **Step 1: Run make lint**

Run: `make lint`
Expected: No errors

- [ ] **Step 2: Fix any lint or type errors**

If `make lint` reports errors, fix them. Common issues:
- Missing imports of `Armor` in files that reference `Player.armor`
- Type mismatches where `bool` was expected but `Armor | None` is now used

- [ ] **Step 3: Run make test**

Run: `make test`
Expected: ALL PASS

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve lint and type check issues"
```

---

### Task 12: Final integration test

**Files:**
- Test: `tests/game/test_engine.py`

- [ ] **Step 1: Write integration test for full equip/swap flow**

Add to `tests/game/test_engine.py`:

```python
class TestEquipSwapIntegration:
    def test_full_weapon_swap_flow(self):
        engine = GameEngine()
        engine.start_game()
        old_weapon_name = engine.state.player.weapon.name
        engine.state.player.inventory.append(
            Item(name="Flail", type=ItemType.WEAPON, damage="d6+1")
        )
        engine.use_item(0)
        assert engine.state.player.weapon.name == "Flail"
        assert any(item.name == old_weapon_name for item in engine.state.player.inventory)

    def test_full_armor_swap_flow(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.armor = Armor(name="Armor", absorb="d4")
        engine.state.player.inventory.append(
            Item(name="Chain Mail", type=ItemType.ARMOR, absorb="d6")
        )
        engine.use_item(0)
        assert engine.state.player.armor.name == "Chain Mail"
        assert any(item.name == "Armor" for item in engine.state.player.inventory)

    def test_buy_armor_then_equip_another(self):
        engine = GameEngine()
        engine.start_game()
        engine.state.player.silver = 30
        engine.state.phase = Phase.SHOP
        engine.buy_item(8)  # Buy Armor
        assert engine.state.player.armor is not None
        assert engine.state.player.armor.name == "Armor"
```

- [ ] **Step 2: Run integration tests**

Run: `uv run pytest tests/game/test_engine.py::TestEquipSwapIntegration -v`
Expected: PASS

- [ ] **Step 3: Run full test suite one more time**

Run: `make test`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tests/game/test_engine.py
git commit -m "test: add integration tests for equip/swap flow"
```