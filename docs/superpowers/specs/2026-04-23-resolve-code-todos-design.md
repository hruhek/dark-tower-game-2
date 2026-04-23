# Design: Resolve 5 Code TODOs

## Date: 2026-04-23

## Context

The DARK FORT codebase has 5 inline TODO comments that have been flagged for cleanup:

| # | File | Line | Description |
|---|------|------|-------------|
| 1 | `game/models.py` | 44 | `Weapon.use()` duplicates inventory-swap logic from `Armor.use()` |
| 2 | `game/models.py` | 65 | `Armor.use()` duplicates inventory-swap logic from `Weapon.use()` |
| 3 | `tui/display.py` | 13 | Empty `# TODO:` with no description |
| 4 | `game/engine.py` | 62 | `cloak_charges` should live on `Cloak`, not `Player` |
| 5 | `game/engine.py` | 79 | Entrance result text is appended but its game effect is not resolved |

These are all self-contained refactorings/bug fixes with no UI changes.

## Goals

1. Eliminate duplication in `Weapon.use()` / `Armor.use()`
2. Remove the empty TODO in `display.py`
3. Move `cloak_charges` from `Player` to `Cloak`
4. Implement game effects for entrance room results

## Non-goals

- No new features (these are cleanup/fixes)
- No UI changes
- No changes to `docs/DARK_FORT.md`

## Design

### 1. Extract equip helper on `Player`

Both `Weapon` and `Armor` follow the exact same equip-swap pattern:

1. If an item is already equipped in that slot, move it to inventory
2. Equip the new item
3. Remove it from inventory at the given index

We add a method to `Player`:

```python
def equip(self, item: Weapon | Armor, index: int) -> list[str]:
    slot_attr = "weapon" if isinstance(item, Weapon) else "armor"
    messages: list[str] = []
    current = getattr(self, slot_attr)
    if current is not None:
        self.inventory.append(current)
        messages.append(f"{current.name} moved to inventory.")
    setattr(self, slot_attr, item)
    messages.append(f"You equip the {item.name}.")
    self.inventory.pop(index)
    return messages
```

Then `Weapon.use()` and `Armor.use()` become thin wrappers:

```python
def use(self, state: GameState, index: int) -> ActionResult:
    messages = state.player.equip(self, index)
    return ActionResult(messages=messages)
```

This keeps state mutation in `Player`, following the architecture rule that `game/` is pure domain logic.

### 2. Remove ghost TODO in `display.py`

Delete the empty `# TODO:` comment on line 13. No code changes.

### 3. Move `cloak_charges` to `Cloak` model

- Add `charges: int = 0` field to `Cloak` model in `game/models.py`
- Remove `cloak_charges: int = 0` field from `Player` model
- In `engine.py:start_game()`, when equipping the starting cloak, set charges on the item itself: `cloak.charges = roll("d4")`
- Search the codebase for any remaining references to `player.cloak_charges` and update them to access `cloak.charges` instead (or remove if the logic no longer makes sense)

### 4. Implement entrance result effects

The `ENTRANCE_RESULTS` table maps to 4 outcomes:

| Roll | Text | Effect |
|------|------|--------|
| 1 | Find a random item | Add a random item to player inventory |
| 2 | A weak monster stands guard | Spawn a weak monster and enter combat phase |
| 3 | A dying mystic gives a random scroll | Add a random scroll to player inventory |
| 4 | The entrance is eerily quiet | No effect |

After rolling the entrance result in `engine.py:start_game()`, add a `match` block:

```python
match entrance_result:
    case 0:  # Find a random item
        item = random.choice(STARTING_ITEMS)
        state.player.inventory.append(item)
    case 1:  # Weak monster stands guard
        monster = random.choice(WEAK_MONSTERS)
        state.combat = CombatState(monster=monster)
        state.phase = Phase.COMBAT
    case 2:  # Dying mystic gives scroll
        scroll = random.choice(SCROLLS)
        state.player.inventory.append(scroll)
    case _:  # Quiet — nothing
        pass
```

Reuse existing engine methods/tables where possible. The entrance result message stays appended to `messages` as-is.

## Testing

- Run `make test` after changes — all existing tests must pass
- Run `make lint` after changes
- No new tests needed for pure refactorings (TODOs 1–3)
- For entrance result resolution (TODO 4), consider adding a test that mocks the roll and asserts the correct effect

## Risks

- Entrance result (TODO 4) changes game start behavior — ensure the new effects don't break existing game flow assumptions in tests
- Cloak charges move (TODO 3) may affect save/load if serialization depends on `Player.cloak_charges` — check if save/load exists
