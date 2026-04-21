# Inventory & Equip System Design

## Goal

Allow the player to carry multiple weapons and armor in inventory, but equip only one weapon and one armor at a time. Equipping a new item swaps the old one back to inventory.

## Approach

**Approach A: Equipped slots** — Add `Armor` model, change `Player.armor` from `bool` to `Armor | None`, add swap logic when equipping.

## Data Models

### New `Armor` model (`models.py`)

```python
class Armor(BaseModel):
    name: str
    absorb: str = "d4"  # dice expression for damage absorption
```

Mirrors `Weapon` — simple Pydantic model with `name` + dice expression.

### Changes to `Player` model (`models.py`)

```python
class Player(BaseModel):
    # ... existing fields unchanged ...
    weapon: Weapon | None = None          # unchanged
    armor: Armor | None = None            # was: bool = False
    inventory: list[Item] = []             # unchanged
    # ... rest unchanged ...
```

`armor: Armor | None` — `None` means no armor equipped (replaces `armor: bool`).

### Changes to `Item` model (`models.py`)

```python
class Item(BaseModel):
    name: str
    type: ItemType
    damage: str | None = None       # weapon damage / potion heal dice
    attack_bonus: int = 0           # weapon to-hit bonus
    absorb: str | None = None       # NEW: armor absorption dice
    uses: int | None = None          # unchanged (still unused)
```

`absorb` field on `Item` parallels `damage` for weapons — used when converting between `Item` and `Armor`.

### Conversion helpers (`models.py` or `rules.py`)

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

## Equip/Swap Logic

### Equipping a weapon (`engine.py` `use_item()`)

1. Player uses a weapon-type item from inventory
2. If `player.weapon` is not `None`, convert current weapon to `Item` via `weapon_to_item()` and append to inventory
3. Create `Weapon` from the item's fields, assign to `player.weapon`
4. Remove the item from inventory
5. Log: "You equip {name}." (and "{old_weapon} moved to inventory." if swapped)

### Equipping armor (`engine.py` `use_item()`)

1. Player uses an armor-type item from inventory
2. If `player.armor` is not `None`, convert current armor to `Item` via `armor_to_item()` and append to inventory
3. Create `Armor` from the item's fields, assign to `player.armor`
4. Remove the item from inventory
5. Log: "You equip {name}." (and "{old_armor} moved to inventory." if swapped)

### Buying armor (`engine.py` `buy_item()`)

- Currently sets `player.armor = True`. Change to create `Armor` object and assign to `player.armor`
- If player already has armor, swap old armor back to inventory (same as equip logic)

### Starting equipment (`rules.py` / `engine.py`)

- When starting item is armor, create `Armor(name="Armor", absorb="d4")` and assign to `player.armor` instead of setting `bool = True`

## Combat Changes

### Fix `weapon.attack_bonus` (`rules.py` `resolve_combat_hit()`)

- Currently: `effective_roll = player_roll + player.attack_bonus`
- Change to: `effective_roll = player_roll + player.attack_bonus + (player.weapon.attack_bonus if player.weapon else 0)`
- This makes weapon attack_bonus actually affect to-hit rolls

### Armor absorption (`rules.py` `resolve_combat_hit()`)

- Currently: `absorbed = roll("d4")` (hardcoded)
- Change to: `absorbed = roll(player.armor.absorb)` (uses armor's dice expression)
- Different armor types absorb different amounts (future expansion)

### Armor table (`tables.py`)

Single entry matching the rules doc:

```python
ARMOR_TABLE: list[Armor] = [
    Armor(name="Armor", absorb="d4"),
]
```

The `Armor` model supports multiple types for future expansion, but only "Armor" exists per the rules.

### Shop items (`tables.py`)

Update `SHOP_ITEMS` armor entry to include `absorb`:

```python
(Item(name="Armor", type=ItemType.ARMOR, absorb="d4"), 10),
```

## TUI Changes

### StatusBar (`widgets.py`)

Add `#armor` label after `#weapon`:
- `Armor: Armor (d4)` when armor equipped
- `Armor: None` when no armor

### Inventory display (`screens.py` `_show_inventory()`)

Show type prefix and stats:
- `1. [W] Sword (d6+1)` for weapons
- `2. [A] Armor (d4)` for armor
- `3. [P] Potion` for potions

### Shop display (`screens.py` `ShopScreen`)

Show armor absorb alongside price (like weapons show damage).

## Edge Cases

1. **Equipping when nothing is currently equipped** — just equip, no swap needed
2. **Buying weapon/armor from shop** — same swap logic applies
3. **Level benefit 5 (Mighty Zweihander)** — adds to inventory as `Item`, player equips later via "use"
4. **Loot drops** — weapons/armor from loot go to inventory, player equips via "use"
5. **Starting equipment** — weapon goes to `player.weapon` slot, armor goes to `player.armor` slot
6. **Migration** — `Player.armor` changes from `bool` to `Armor | None`. All test fixtures using `armor=True` must be updated to `armor=Armor(name="Armor", absorb="d4")`.

## Files to Modify

- `src/dark_fort/game/models.py` — Add `Armor` model, change `Player.armor`, add `Item.absorb`, add conversion helpers
- `src/dark_fort/game/rules.py` — Fix `weapon.attack_bonus` in combat, use `armor.absorb` instead of hardcoded `d4`, update `generate_starting_equipment()`
- `src/dark_fort/game/engine.py` — Update `use_item()`, `buy_item()`, `start_game()` for new equip/swap logic
- `src/dark_fort/game/tables.py` — Add `ARMOR_TABLE`, update `SHOP_ITEMS` armor entry
- `src/dark_fort/tui/widgets.py` — Add armor label to StatusBar
- `src/dark_fort/tui/screens.py` — Update inventory display and shop display
- `tests/` — Update all test fixtures for `armor` field change, add tests for equip/swap logic