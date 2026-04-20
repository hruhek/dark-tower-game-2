# Dark Fort Screen Mocks

## Title Screen

Widget tree:
```
Screen: TitleScreen
├── Static (classes="title-header") — "DARK FORT"
├── Static (classes="title-subtitle") — "A delve into the catacombs"
└── Static (classes="title-footer") — "Press ENTER to begin"
```

Key bindings: `Enter` → start game

## Game Screen

Widget tree:
```
Screen: GameScreen
├── StatusBar (Horizontal)
│   ├── Label#hp — "HP: 15/15"
│   ├── Label#silver — "Silver: 18"
│   ├── Label#points — "Points: 5"
│   ├── Label#rooms — "Rooms: 3/12"
│   └── Label#weapon — "Weapon: Warhammer (d6)"
├── LogView#log (RichLog) — scrollable event log
└── CommandBar#commands (Horizontal)
    └── Button per Command enum (context-sensitive)
```

Context-sensitive commands:
- Combat: [Attack] [Flee] [Use Item]
- Exploring: [Explore] [Inventory]
- Shop: [Browse] [Leave]

## Shop Screen

Widget tree:
```
Screen: ShopScreen
├── Header
├── Static (classes="title-header") — "The Void Peddler"
├── LogView#shop-log — item list with prices
└── CommandBar#commands
    └── Button: "Leave"
```

Key bindings: `1-9` → buy item, `L` → leave

## Game Over Screen

Widget tree:
```
Screen: GameOverScreen
├── Static (classes="game-over-header") — "YOU HAVE FALLEN" / "VICTORY"
├── Static (classes="game-over-stats") — "Rooms explored: N"
├── Static (classes="game-over-stats") — "Points gathered: N/15"
├── Static (classes="game-over-stats") — "Silver: N"
└── Static (classes="game-over-footer") — "Press ENTER to try again"
```

Key bindings: `Enter` → restart
