from enum import Enum

class Rune():
    """
    a class of runes
    """
    __slots__ = ['rune', 'race', 'min_match', 'untouchable', 'must_remove', 'no_first', 'all_first']

    def __init__(self, rune: int = 0, race: int = 0, untouchable: bool = False, must_remove: bool = False):
        self.rune = rune
        self.untouchable = untouchable
        self.must_remove = must_remove
        self.race = race
        self.min_match = 3
        self.no_first = False
        self.all_first = False
    
    def __hash__(self) -> int:
        return hash(self.rune)
    
    def __eq__(self, other) -> bool:
        return self.rune == other.rune
    
    def __repr__(self) -> str:
        return f'Rune({self.rune}, {self.race}, {self.untouchable}, {self.must_remove})'


class Runes(Enum):
    """A class of runes"""
    EMPTY = 0
    WATER = 1
    FIRE = 2
    WOOD = 3
    LIGHT = 4
    DARK = 5
    HEART = 6
    HIDDEN = 7
    UNELIMINABLE = 8
    UNKNOWN = 9
    
    @staticmethod
    def int2str(rune: int) -> str:
        for r in Runes:
            if r.value == rune:
                return r.name
        return 'invalid rune'
    
    @staticmethod
    def int2color_code(rune: int) -> str:
        if rune == Runes.EMPTY.value:
            return "\033[0m" # white
        if rune == Runes.WATER.value:
            return "\033[94m" # blue
        if rune == Runes.FIRE.value:
            return "\033[91m" # red
        if rune == Runes.WOOD.value:
            return "\033[92m" # green
        if rune == Runes.LIGHT.value:
            return "\033[93m" # yellow
        if rune == Runes.DARK.value:
            return "\033[95m" # magenta
        if rune == Runes.HEART.value:
            return "\033[0m" # white
        if rune == Runes.HIDDEN.value or rune == Runes.UNELIMINABLE.value:
            return "\033[0m" # white
        if rune == Runes.UNKNOWN.value:
            return "\033[91m" # red
        raise ValueError(f'Invalid rune: {rune}')
    
    @staticmethod
    def str2int(s: str) -> int:
        if s == 'WATER' or s == 'water' or s == 'Water' or s == 'w' or s == 'W':
            return Runes.WATER.value
        elif s == 'FIRE' or s == 'fire' or s == 'Fire' or s == 'f' or s == 'F':
            return Runes.FIRE.value
        elif s == 'GRASS' or s == 'grass' or s == 'Grass' or s == 'g' or s == 'G':
            return Runes.WOOD.value
        elif s == 'LIGHT' or s == 'light' or s == 'Light' or s == 'l' or s == 'L':
            return Runes.LIGHT.value
        elif s == 'DARK' or s == 'dark' or s == 'Dark' or s == 'd' or s == 'D':
            return Runes.DARK.value
        elif s == 'HEART' or s == 'heart' or s == 'Heart' or s == 'h' or s == 'H':
            return Runes.HEART.value
        elif s == 'HIDDEN' or s == 'hidden' or s == 'Hidden' or s == 'q' or s == 'Q':
            return Runes.HIDDEN.value
        elif s == 'UNELIMINABLE' or s == 'uneliminable' or s == 'Uneliminable' or s == 'u' or s == 'U':
            return Runes.UNELIMINABLE.value
        else:
            return Runes.UNKNOWN.value