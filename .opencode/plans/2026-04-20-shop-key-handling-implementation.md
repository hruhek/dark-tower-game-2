# Fix Shop Key Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix digit key presses not registering in ShopScreen and make item 10 accessible via "0" key.

**Architecture:** The root cause is focus management — at runtime, focus lands on a child widget (Header, LogView, or Button) instead of the Screen, so key events never reach `ShopScreen.on_key`. The fix is to ensure the Screen has focus on mount and that child widgets that don't need focus can't steal it. We also remap "0" to index 9 (item 10) and update the help text.

**Tech Stack:** Python, Textual, pytest

---

### Task 1: Fix focus management in ShopScreen

**Files:**
- Modify: `src/dark_fort/tui/screens.py:165-169` (compose method)
- Modify: `src/dark_fort/tui/screens.py:171-189` (on_mount method)

- [ ] **Step 1: Make Header and LogView non-focusable in ShopScreen.compose**

In `src/dark_fort/tui/screens.py`, modify the `compose` method to set `can_focus=False` on Header and LogView so they can't steal focus:

```python
def compose(self) -> ComposeResult:
    yield Header(show_clock=False)
    yield Static("The Void Peddler", classes="title-header")
    log = LogView(id="shop-log")
    log.can_focus = False
    yield log
    yield CommandBar(id="commands", commands=[Command.LEAVE])
```

- [ ] **Step 2: Add self.focus() to ShopScreen.on_mount**

In `src/dark_fort/tui/screens.py`, add `self.focus()` at the end of `on_mount` so the Screen itself has focus after setup:

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
    log.add_message("Press 1-9, 0 for item 10, or L to leave.")
    self.focus()
```

Note: The help text is also updated here from `"Press a number (1-10) to buy, or L to leave."` to `"Press 1-9, 0 for item 10, or L to leave."`.

- [ ] **Step 3: Run existing tests to verify nothing is broken**

Run: `uv run pytest tests/tui/test_screens.py::TestShopScreen -v`
Expected: All 3 existing ShopScreen tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/dark_fort/tui/screens.py
git commit -m "fix: add focus management to ShopScreen so digit keys register"
```

---

### Task 2: Map "0" key to item 10 and add test

**Files:**
- Modify: `src/dark_fort/tui/screens.py:203-212` (on_key method)
- Modify: `tests/tui/test_screens.py` (add test)

- [ ] **Step 1: Write the failing test for "0" key buying item 10**

In `tests/tui/test_screens.py`, add a new test method to the `TestShopScreen` class:

```python
async def test_buy_item_10_with_zero_key(self):
    async with DarkFortApp().run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        pilot.app.engine.state.player.silver = 20  # ty: ignore[unresolved-attribute]
        pilot.app.engine.state.phase = Phase.SHOP  # ty: ignore[unresolved-attribute]
        pilot.app.push_screen(ShopScreen(engine=pilot.app.engine))  # ty: ignore[unresolved-attribute]
        await pilot.pause()
        await pilot.press("0")
        await pilot.pause()
        assert pilot.app.engine.state.player.silver == 5  # ty: ignore[unresolved-attribute]  # 20 - 15 (Cloak price)
        assert any(
            "Cloak" in item.name
            for item in pilot.app.engine.state.player.inventory  # ty: ignore[unresolved-attribute]
        )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/tui/test_screens.py::TestShopScreen::test_buy_item_10_with_zero_key -v`
Expected: FAIL — pressing "0" currently maps to index -1 which is out of range, so no purchase happens and silver stays at 20.

- [ ] **Step 3: Update on_key to map "0" to index 9**

In `src/dark_fort/tui/screens.py`, modify the `on_key` method:

```python
def on_key(self, event) -> None:
    if event.character and event.character.isdigit():
        digit = int(event.character)
        index = digit - 1 if digit != 0 else 9
        if index < 0 or index >= len(SHOP_ITEMS):
            return
        result = self.engine.buy_item(index)
        log = self.query_one("#shop-log", LogView)
        for msg in result.messages:
            log.add_message(msg)
        log.add_message(f"\nYour silver: {self.engine.state.player.silver}s")
```

- [ ] **Step 4: Run all ShopScreen tests to verify they pass**

Run: `uv run pytest tests/tui/test_screens.py::TestShopScreen -v`
Expected: All 4 ShopScreen tests PASS (3 existing + 1 new)

- [ ] **Step 5: Run full test suite and lint**

Run: `make test && make lint`
Expected: All tests pass, lint clean

- [ ] **Step 6: Commit**

```bash
git add src/dark_fort/tui/screens.py tests/tui/test_screens.py
git commit -m "fix: map 0 key to item 10 in shop and add test"
```