# Fix Enum Usage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all bare-string comparisons against `ItemType` and `Phase` enum fields with proper enum member references.

**Architecture:** Keep all `StrEnum` definitions in `enums.py` unchanged. In `engine.py`, convert multi-branch `if`/`elif` chains on `item.type` to `match`/`case` on `ItemType`. In `screens.py`, replace bare-string comparisons with `ItemType`/`Phase` members and convert the `type_prefix` dict to use `ItemType` enum keys.

**Tech Stack:** Python 3.13, StrEnum, Pydantic, pytest, ruff, ty

---

### Task 1: Fix `engine.py` — `start_game()` bare-string comparisons

**Files:**
- Modify: `src/dark_fort/game/engine.py`

**Context:** Line 4 imports only `Phase`. Need to add `ItemType`. Lines 51-56 use bare strings `"armor"`, `"potion"`, `"scroll"`, `"cloak"`.

- [ ] **Step 1: Add `ItemType` to the import**

Change line 4 from:
```python
from dark_fort.game.enums import Phase
```
to:
```python
from dark_fort.game.enums import ItemType, Phase
```

- [ ] **Step 2: Replace the `if`/`elif` chain in `start_game()` with `match`/`case`**

Replace lines 51-56:
```python
        if item.type == "armor":
            self.state.player.armor = Armor(name=item.name, absorb=item.absorb or "d4")
        elif item.type == "potion" or item.type == "scroll":
            self.state.player.inventory.append(item)
        elif item.type == "cloak":
            self.state.player.cloak_charges = roll("d4")
```

With:
```python
        match item.type:
            case ItemType.ARMOR:
                self.state.player.armor = Armor(name=item.name, absorb=item.absorb or "d4")
            case ItemType.POTION | ItemType.SCROLL:
                self.state.player.inventory.append(item)
            case ItemType.CLOAK:
                self.state.player.cloak_charges = roll("d4")
```

- [ ] **Step 3: Run tests to verify**

Run: `make test`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/dark_fort/game/engine.py
git commit -m "refactor(engine): use ItemType enum in start_game match/case"
```

---

### Task 2: Fix `engine.py` — `buy_item()` bare-string comparisons

**Files:**
- Modify: `src/dark_fort/game/engine.py`

**Context:** Lines 149-168 use bare strings `"armor"`, `"cloak"`, `"scroll"`.

- [ ] **Step 1: Replace the `if`/`elif` chain in `buy_item()` with `match`/`case`**

Replace lines 149-172:
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
        elif item.type == "cloak":
            self.state.player.cloak_charges = roll("d4")
            msg = f"You buy {item.name} for {price}s ({self.state.player.cloak_charges} charges)."
        elif item.type == "scroll":
            from dark_fort.game.tables import SCROLLS_TABLE

            scroll_name, _, _ = SCROLLS_TABLE[roll("d4") - 1]
            self.state.player.inventory.append(Item(name=scroll_name, type=item.type))
            msg = f"You buy {scroll_name} for {price}s."
        else:
            self.state.player.inventory.append(item)
            msg = f"You buy {item.name} for {price}s."
```

With:
```python
        match item.type:
            case ItemType.ARMOR:
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
            case ItemType.CLOAK:
                self.state.player.cloak_charges = roll("d4")
                msg = f"You buy {item.name} for {price}s ({self.state.player.cloak_charges} charges)."
            case ItemType.SCROLL:
                from dark_fort.game.tables import SCROLLS_TABLE

                scroll_name, _, _ = SCROLLS_TABLE[roll("d4") - 1]
                self.state.player.inventory.append(Item(name=scroll_name, type=item.type))
                msg = f"You buy {scroll_name} for {price}s."
            case _:
                self.state.player.inventory.append(item)
                msg = f"You buy {item.name} for {price}s."
```

- [ ] **Step 2: Run tests to verify**

Run: `make test`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add src/dark_fort/game/engine.py
git commit -m "refactor(engine): use ItemType enum in buy_item match/case"
```

---

### Task 3: Fix `engine.py` — `use_item()` bare-string comparisons

**Files:**
- Modify: `src/dark_fort/game/engine.py`

**Context:** Lines 193-238 use bare strings `"potion"`, `"scroll"`, `"weapon"`, `"armor"`, `"cloak"`.

- [ ] **Step 1: Replace the `if`/`elif` chain in `use_item()` with `match`/`case`**

Replace lines 193-239:
```python
        if item.type == "potion":
            heal = roll(item.damage or "d6")
            self.state.player.hp = min(
                self.state.player.hp + heal, self.state.player.max_hp
            )
            messages.append(f"You drink the potion and heal {heal} HP.")
            self.state.player.inventory.pop(index)

        elif item.type == "scroll":
            messages.append(f"You unroll the {item.name}...")
            self.state.player.inventory.pop(index)

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

        elif item.type == "cloak":
            self.state.player.cloak_charges = max(
                0, self.state.player.cloak_charges - 1
            )
            messages.append(
                f"Cloak activated. {self.state.player.cloak_charges} charges remaining."
            )

        return ActionResult(messages=messages)
```

With:
```python
        match item.type:
            case ItemType.POTION:
                heal = roll(item.damage or "d6")
                self.state.player.hp = min(
                    self.state.player.hp + heal, self.state.player.max_hp
                )
                messages.append(f"You drink the potion and heal {heal} HP.")
                self.state.player.inventory.pop(index)

            case ItemType.SCROLL:
                messages.append(f"You unroll the {item.name}...")
                self.state.player.inventory.pop(index)

            case ItemType.WEAPON:
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

            case ItemType.ARMOR:
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

            case ItemType.CLOAK:
                self.state.player.cloak_charges = max(
                    0, self.state.player.cloak_charges - 1
                )
                messages.append(
                    f"Cloak activated. {self.state.player.cloak_charges} charges remaining."
                )

        return ActionResult(messages=messages)
```

- [ ] **Step 2: Run tests to verify**

Run: `make test`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add src/dark_fort/game/engine.py
git commit -m "refactor(engine): use ItemType enum in use_item match/case"
```

---

### Task 4: Fix `screens.py` — Phase comparisons and ItemType comparisons

**Files:**
- Modify: `src/dark_fort/tui/screens.py`

**Context:** Line 8 imports only `Command`. Lines 68-72, 120-138, 145-151, 180-187 use bare-string comparisons against Phase and ItemType values.

- [ ] **Step 1: Add `ItemType` and `Phase` to the import**

Change line 8 from:
```python
from dark_fort.game.enums import Command
```
to:
```python
from dark_fort.game.enums import Command, ItemType, Phase
```

- [ ] **Step 2: Replace bare-string Phase comparisons in `_update_commands()`**

Replace lines 68-73:
```python
        if phase == "combat":
            commands = [Command.ATTACK, Command.FLEE, Command.USE_ITEM]
        elif phase == "exploring":
            commands = [Command.EXPLORE, Command.INVENTORY]
        elif phase == "shop":
            commands = [Command.BROWSE, Command.LEAVE]
```

With:
```python
        if phase == Phase.COMBAT:
            commands = [Command.ATTACK, Command.FLEE, Command.USE_ITEM]
        elif phase == Phase.EXPLORING:
            commands = [Command.EXPLORE, Command.INVENTORY]
        elif phase == Phase.SHOP:
            commands = [Command.BROWSE, Command.LEAVE]
```

- [ ] **Step 3: Update `type_prefix` dict and bare-string comparisons in `_show_inventory()`**

Replace lines 120-138:
```python
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
```

With:
```python
        type_prefix = {
            ItemType.WEAPON: "W",
            ItemType.ARMOR: "A",
            ItemType.POTION: "P",
            ItemType.SCROLL: "S",
            ItemType.ROPE: "R",
            ItemType.CLOAK: "C",
        }
        messages = ["Inventory:"]
        for i, item in enumerate(player.inventory):
            prefix = type_prefix.get(item.type, "?")
            stats = ""
            if item.type == ItemType.WEAPON and item.damage:
                stats = f" ({item.damage})"
            elif item.type == ItemType.ARMOR and item.absorb:
                stats = f" ({item.absorb})"
            elif item.type == ItemType.POTION and item.damage:
                stats = f" (heal {item.damage})"
            messages.append(f"  {i + 1}. [{prefix}] {item.name}{stats}")
```

- [ ] **Step 4: Replace bare-string Phase comparisons in `_handle_phase_change()`**

Replace lines 145-153:
```python
        if result.phase == "game_over":
            self.dismiss()
            self.app.push_screen(GameOverScreen(engine=self.engine))
        elif result.phase == "victory":
            self.dismiss()
            self.app.push_screen(GameOverScreen(engine=self.engine, victory=True))
        elif result.phase == "shop":
            self.dismiss()
            self.app.push_screen(ShopScreen(engine=self.engine))
```

With:
```python
        if result.phase == Phase.GAME_OVER:
            self.dismiss()
            self.app.push_screen(GameOverScreen(engine=self.engine))
        elif result.phase == Phase.VICTORY:
            self.dismiss()
            self.app.push_screen(GameOverScreen(engine=self.engine, victory=True))
        elif result.phase == Phase.SHOP:
            self.dismiss()
            self.app.push_screen(ShopScreen(engine=self.engine))
```

- [ ] **Step 5: Replace bare-string ItemType comparisons in `ShopScreen.on_mount()`**

Replace lines 180-188:
```python
            if item.type == "weapon" and item.damage:
                stats = f" ({item.damage}"
                if item.attack_bonus:
                    stats += f"/+{item.attack_bonus}"
                stats += ")"
            elif item.type == "armor" and item.absorb:
                stats = f" (-{item.absorb})"
            elif item.type == "potion" and item.damage:
                stats = f" (heal {item.damage})"
```

With:
```python
            if item.type == ItemType.WEAPON and item.damage:
                stats = f" ({item.damage}"
                if item.attack_bonus:
                    stats += f"/+{item.attack_bonus}"
                stats += ")"
            elif item.type == ItemType.ARMOR and item.absorb:
                stats = f" (-{item.absorb})"
            elif item.type == ItemType.POTION and item.damage:
                stats = f" (heal {item.damage})"
```

- [ ] **Step 6: Run tests to verify**

Run: `make test`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/dark_fort/tui/screens.py
git commit -m "refactor(screens): use Phase and ItemType enum members instead of bare strings"
```

---

### Task 5: Verify no remaining bare-string enum comparisons

**Files:** None — verification only

- [ ] **Step 1: Search for remaining bare-string comparisons against enum-typed fields**

Run:
```bash
rg '== "' src/dark_fort/game/engine.py src/dark_fort/game/rules.py src/dark_fort/tui/screens.py src/dark_fort/tui/widgets.py
```

Expected: No matches for `item.type == "`, `phase == "`, `result.phase == "` patterns. The only bare-string comparisons should be `monster.special ==` and `room_result ==` in `rules.py` (these are plain `str` fields, not enums).

- [ ] **Step 2: Run full lint and typecheck**

Run: `make lint`
Expected: No errors.

- [ ] **Step 3: Run full test suite**

Run: `make test`
Expected: All tests pass.

---

### Self-Review

1. **Spec coverage:** All bare-string enum comparisons identified in the design are covered by Tasks 1-4. Task 5 verifies completeness.
2. **Placeholder scan:** No TBDs or TODOs. All code is explicit.
3. **Type consistency:** `ItemType` and `Phase` imports match their usage throughout. `match`/`case` uses the correct enum member syntax.
4. **Scope:** Focused solely on replacing bare-string enum comparisons. No unrelated refactoring.

**Note on linting:** There is no ruff rule for catching bare-string comparisons against `StrEnum` fields. Since `StrEnum` inherits from `str`, type checkers also won't flag this. The enforcement strategy is structural: `match`/`case` in `engine.py` naturally uses enum members, and the TUI layer now uses explicit `ItemType.X` / `Phase.X` references. Future developers should follow these patterns.
