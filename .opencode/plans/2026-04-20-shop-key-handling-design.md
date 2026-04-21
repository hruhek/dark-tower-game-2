# Fix Shop Key Handling

## Problem

Digit key presses (1-9, 0) don't register in the ShopScreen at runtime. The `on_key` handler exists and tests pass, but at runtime focus lands on a child widget (Header, LogView, or Button) instead of the Screen, preventing key events from reaching `ShopScreen.on_key`.

Additionally, item 10 (Cloak of invisibility) is unreachable via keyboard because pressing "0" maps to index -1.

## Solution

### 1. Fix focus management

In `ShopScreen.on_mount()`, call `self.focus()` so the Screen itself has focus and receives key events. Set `can_focus=False` on the LogView and Header widgets to prevent them from stealing focus.

### 2. Map "0" to item 10

In `ShopScreen.on_key()`, change the index calculation:

```python
digit = int(event.character)
index = (digit - 1) if digit != 0 else 9
```

### 3. Update help text

Change the shop log message from `"Press a number (1-10) to buy, or L to leave."` to `"Press 1-9, 0 for item 10, or L to leave."`.

### 4. Add test for "0" key

Add a test that verifies pressing "0" buys item 10 (Cloak of invisibility).

## Files to change

- `src/dark_fort/tui/screens.py` — ShopScreen: focus fix, key mapping, help text
- `src/dark_fort/tui/styles.tcss` — Optionally add `can_focus: false` for Header/LogView
- `tests/tui/test_screens.py` — Add test for "0" key buying item 10