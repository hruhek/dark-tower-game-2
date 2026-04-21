from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator

from dark_fort.game.enums import (
    Command,
    ItemType,
    MonsterSpecial,
    MonsterTier,
    Phase,
    ScrollType,
)


class Item(BaseModel):
    name: str


class Weapon(Item):
    type: Literal[ItemType.WEAPON] = ItemType.WEAPON
    damage: str
    attack_bonus: int = 0


class Armor(Item):
    type: Literal[ItemType.ARMOR] = ItemType.ARMOR
    absorb: str = "d4"


class Potion(Item):
    type: Literal[ItemType.POTION] = ItemType.POTION
    heal: str


class Scroll(Item):
    type: Literal[ItemType.SCROLL] = ItemType.SCROLL
    scroll_type: ScrollType


class Rope(Item):
    type: Literal[ItemType.ROPE] = ItemType.ROPE


class Cloak(Item):
    type: Literal[ItemType.CLOAK] = ItemType.CLOAK


AnyItem = Annotated[
    Weapon | Armor | Potion | Scroll | Rope | Cloak,
    Field(discriminator="type"),
]


class Monster(BaseModel):
    name: str
    tier: MonsterTier
    points: int
    damage: str
    hp: int
    loot: str | None = None
    special: MonsterSpecial | None = None


class Player(BaseModel):
    name: str = "Kargunt"
    hp: int = 15
    max_hp: int = 15
    silver: int = 0
    points: int = 0
    weapon: Weapon | None = None
    armor: Armor | None = None
    inventory: list[AnyItem] = Field(default_factory=list)
    cloak_charges: int = 0
    attack_bonus: int = 0
    level_benefits: list[int] = Field(default_factory=list)
    daemon_fights_remaining: int = 0

    @field_validator("level_benefits")
    @classmethod
    def level_benefits_must_be_unique(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("level_benefits must contain unique values")
        return v


class Room(BaseModel):
    id: int
    shape: str
    doors: int
    result: str
    explored: bool = False
    connections: list[int] = Field(default_factory=list)


class CombatState(BaseModel):
    monster: Monster
    monster_hp: int
    player_turns: int = 0
    daemon_assist: bool = False


class GameState(BaseModel):
    player: Player = Field(default_factory=Player)
    current_room: Room | None = None
    rooms: dict[int, Room] = Field(default_factory=dict)
    phase: Phase
    combat: CombatState | None = None
    level_up_queue: bool = False
    log: list[str] = Field(default_factory=list)


class ActionResult(BaseModel):
    messages: list[str]
    phase: Phase | None = None
    choices: list[Command] = Field(default_factory=list)
    state_delta: dict[str, Any] = Field(default_factory=dict)
