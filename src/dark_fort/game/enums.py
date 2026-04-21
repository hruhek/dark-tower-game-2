from enum import StrEnum, auto


class ItemType(StrEnum):
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    SCROLL = auto()
    ROPE = auto()
    CLOAK = auto()


class MonsterTier(StrEnum):
    WEAK = auto()
    TOUGH = auto()


class Phase(StrEnum):
    TITLE = auto()
    ENTRANCE = auto()
    EXPLORING = auto()
    COMBAT = auto()
    SHOP = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Command(StrEnum):
    ATTACK = auto()
    FLEE = auto()
    USE_ITEM = auto()
    EXPLORE = auto()
    INVENTORY = auto()
    MOVE = auto()
    BROWSE = auto()
    LEAVE = auto()
    BUY = auto()


class ScrollType(StrEnum):
    SUMMON_DAEMON = auto()
    SOUTHERN_GATE = auto()
    AEGIS_OF_SORROW = auto()
    FALSE_OMEN = auto()


class RoomEvent(StrEnum):
    EMPTY = "Nothing. Explored."
    PIT_TRAP = "Pit trap"
    SOOTHSAYER = "Riddling Soothsayer"
    WEAK_MONSTER = "Weak monster"
    TOUGH_MONSTER = "Tough monster"
    SHOP = "Void Peddler"
