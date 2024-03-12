from enum import Enum

class MoveDir(Enum):
    """A class of move direction"""
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    L_UP = 4
    R_UP = 5
    L_DOWN = 6
    R_DOWN = 7
    NONE = 8
    
    @staticmethod
    def opposite(dir: int) -> int:
        match dir:
            case MoveDir.LEFT.value: return MoveDir.RIGHT.value
            case MoveDir.L_UP.value: return MoveDir.R_DOWN.value
            case MoveDir.UP.value: return MoveDir.DOWN.value
            case MoveDir.R_UP.value: return MoveDir.L_DOWN.value
            case MoveDir.L_DOWN.value: return MoveDir.R_UP.value
            case MoveDir.DOWN.value: return MoveDir.UP.value
            case MoveDir.R_DOWN.value: return MoveDir.L_UP.value
            case MoveDir.RIGHT.value: return MoveDir.LEFT.value
            case MoveDir.NONE.value: return MoveDir.NONE.value
            case _: return MoveDir.NONE.value

    @staticmethod
    def int2str(dir: int) -> str:
        match dir:
            case MoveDir.LEFT.value: return 'L'
            case MoveDir.RIGHT.value: return 'R'
            case MoveDir.UP.value: return 'U'
            case MoveDir.DOWN.value: return 'D'
            case MoveDir.L_UP.value: return 'LU'
            case MoveDir.R_UP.value: return 'RU'
            case MoveDir.L_DOWN.value: return 'LD'
            case MoveDir.R_DOWN.value: return 'RD'
            case _: return 'NON'

    @staticmethod
    def str2int(s: str) -> int:
        if s == 'U':
            return MoveDir.UP.value
        elif s == 'D':
            return MoveDir.DOWN.value
        elif s == 'L':
            return MoveDir.LEFT.value
        elif s == 'R':
            return MoveDir.RIGHT.value
        elif s == 'LU':
            return MoveDir.L_UP.value
        elif s == 'LD':
            return MoveDir.L_DOWN.value
        elif s == 'RU':
            return MoveDir.R_UP.value
        elif s == 'RD':
            return MoveDir.R_DOWN.value
        else:
            return MoveDir.NONE.value
