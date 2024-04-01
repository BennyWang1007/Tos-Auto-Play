import os
import time
# import psutil
import numpy as np

from MoveDir import MoveDir
from Runes import Runes, Rune
from ppadb.client import Client
from ppadb.device import Device as AdbDevice
from constant import *


def get_grid_loc(x, y):
    return LEFT_TOP[0] + x * RUNE_SIZE, LEFT_TOP[1] + y * RUNE_SIZE


def MoveDir2str(dir: int) -> str:
    """convert MoveDir to string"""
    for d in MoveDir:
        if d.value == dir:
            return d.name
    raise ValueError('invalid direction')


def int2MoveDir(dir: int) -> MoveDir:
    """convert int to MoveDir"""
    for d in MoveDir:
        if d.value == dir:
            return d
    raise ValueError('invalid direction')


def int2MoveDir_str(dir: int) -> str:
    """convert int to MoveDir string"""
    for d in MoveDir:
        if d.value == dir:
            return d.name
    raise ValueError('invalid direction')


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f'{func.__name__} elapsed time: {elapsed}')
        return result
    return wrapper


# def set_process_priority():
#     p = psutil.Process(os.getpid())
#     p.nice(psutil.HIGH_PRIORITY_CLASS)


def drop_indices(board_indices: np.ndarray) -> np.ndarray:
    """
    Drop the runes that are eliminated and fill the empty spaces.
    """
    # new_board_indices = board_indices.copy()
    # for x in range(COL_NUM):
    #     new_col = []
    #     for y in range(ROW_NUM):
    #         if board_indices[y, x] != COL_NUM * ROW_NUM:
    #             new_col.append(board_indices[y, x])
    #     new_col = [COL_NUM * ROW_NUM] * (ROW_NUM - len(new_col)) + new_col
    #     new_board_indices[:, x] = new_col
    empty_idx = COL_NUM * ROW_NUM
    # new_board_indices = np.zeros((ROW_NUM, COL_NUM), dtype=int)
    # for x in range(COL_NUM):
    #     cur_y = ROW_NUM - 1
    #     for y in range(ROW_NUM-1, -1, -1):
    #         if board_indices[y, x] != empty_idx:
    #             new_board_indices[cur_y, x] = board_indices[y, x]
    #             cur_y -= 1
    #     for y in range(cur_y, -1, -1):
    #         new_board_indices[y, x] = empty_idx
    for x in range(COL_NUM):
        cur_y = ROW_NUM - 1
        for y in range(ROW_NUM-1, -1, -1):
            if board_indices[y, x] != empty_idx:
                board_indices[cur_y, x] = board_indices[y, x]
                cur_y -= 1
        for y in range(cur_y, -1, -1):
            board_indices[y, x] = empty_idx
    return board_indices


def eliminate_once_with_indices(board: list[Rune], board_indices: np.ndarray, has_setting=False) -> tuple[int, int]:
    # print('Eliminating...')
    # print_board(board, board_indices)
    """
    board: a 1D list of Rune objects, end with a NONE_RUNE
    board_indices: a 2D numpy array of integers, representing the indices of the board
    """
    to_eliminate = np.zeros((ROW_NUM, COL_NUM), dtype=int)
    if not has_setting:
        for y in range(ROW_NUM):
            for x in range(COL_NUM-2):
                rune = board[board_indices[y, x]].rune
                if rune == board[board_indices[y, x+1]].rune and rune == board[board_indices[y, x+2]].rune:
                    to_eliminate[y, x] = to_eliminate[y, x+1] = to_eliminate[y, x+2] = rune

        for i in range(ROW_NUM-2):
            for j in range(COL_NUM):
                rune = board[board_indices[i, j]].rune
                if rune == board[board_indices[i+1, j]].rune and rune == board[board_indices[i+2, j]].rune:
                    to_eliminate[i, j] = to_eliminate[i+1, j] = to_eliminate[i+2, j] = rune
    else:
        # print('has_setting')
        for y in range(ROW_NUM):
            for x in range(COL_NUM):
                min_match = board[board_indices[y, x]].min_match
                # print(f'{min_match}', end=' ')
                rune = board[board_indices[y, x]].rune
                if min_match == 1 or min_match == 2:
                    if min_match == 1: to_eliminate[y, x] = rune
                    if ((x > 0 and board[board_indices[y, x-1]].rune == rune)):
                        to_eliminate[y, x] = to_eliminate[y, x-1] = rune
                    if ((y > 0 and board[board_indices[y-1, x]].rune == rune)):
                        to_eliminate[y, x] = to_eliminate[y-1, x] = rune
                    if ((x < COL_NUM-1 and board[board_indices[y, x+1]].rune == rune)):
                        to_eliminate[y, x] = to_eliminate[y, x+1] = rune
                    if ((y < ROW_NUM-1 and board[board_indices[y+1, x]].rune == rune)):
                        to_eliminate[y, x] = to_eliminate[y+1, x] = rune
                elif min_match == 3:
                    if ((x > 0 and x < COL_NUM-1 and board[board_indices[y, x-1]].rune == rune and board[board_indices[y, x+1]].rune == rune)
                        or (y > 0 and y < ROW_NUM-1 and board[board_indices[y-1, x]].rune == rune and board[board_indices[y+1, x]].rune == rune)
                    ):
                        to_eliminate[y, x] = to_eliminate[y, x-1] = to_eliminate[y, x+1] = rune
                else:
                    raise ValueError('invalid min_match')
    
    combo = 0
    total_eliminated = 0

    
    isZero = False
    idx = (0, 0)
    target = 0
    last_y = 0
    while not isZero:
        isZero = True
        for y in range(last_y, ROW_NUM):
            for x in range(COL_NUM):
                if to_eliminate[y, x] != 0:
                    isZero = False
                    last_y = y
                    idx = (y, x)
                    target = board[board_indices[y, x]].rune
                    # print(f'{idx=}, {target=}')
                    break
            if not isZero: break
        if isZero: break
        combo += 1
        stack = [idx]
        visited = []
        while stack:
            y, x = stack.pop()
            if (y, x) in visited: continue
            visited.append((y, x))
            if y > 0 and to_eliminate[y-1, x] and board[board_indices[y-1, x]].rune == target:
                stack.append((y-1, x))
            if y < ROW_NUM-1 and to_eliminate[y+1, x] and board[board_indices[y+1, x]].rune == target:
                stack.append((y+1, x))
            if x > 0 and to_eliminate[y, x-1] and board[board_indices[y, x-1]].rune == target:
                stack.append((y, x-1))
            if x < COL_NUM-1 and to_eliminate[y, x+1] and board[board_indices[y, x+1]].rune == target:
                stack.append((y, x+1))

        for y, x in visited:
            to_eliminate[y, x] = False
            board_indices[y, x] = COL_NUM * ROW_NUM
            total_eliminated += 1
    # print(f'{combo=}, {total_eliminated=}\n')
    # print_board(board, board_indices)

    return combo, total_eliminated
            

def evaluate_with_indices(board: list[Rune], board_indices: np.ndarray|None = None, has_setting=False) -> tuple[int, int, int, np.ndarray]:
    """
    Evaluate the board with the indices of the board.
    """
    if board_indices is None:
        board_indices = np.reshape(np.arange(COL_NUM * ROW_NUM), (ROW_NUM, COL_NUM))
    
    combo, total_eliminated = eliminate_once_with_indices(board, board_indices, has_setting)
    return combo, combo, total_eliminated, board_indices
    indices_after_first_elimination = board_indices.copy()
    board_indices = drop_indices(board_indices)
    
    if combo == 0:
        return 0, 0, 0, indices_after_first_elimination
    
    f_c = combo
    c = 0
    eli = 0

    while combo > 0:
        c += combo
        eli += total_eliminated
        combo, total_eliminated = eliminate_once_with_indices(board, board_indices, has_setting)
        board_indices = drop_indices(board_indices)

    return f_c, c, eli, indices_after_first_elimination

def print_board(board: list[Rune], indices: np.ndarray|None = None) -> None:

    if indices is None:
        indices = np.array([[x + y * COL_NUM for x in range(COL_NUM)] for y in range(ROW_NUM)])
    if indices is not None:
        assert indices.shape == (ROW_NUM, COL_NUM), 'invalid indices shape'
    
    # print('')
    for y in range(ROW_NUM):
        print('\033[0m|', end=' ')
        for x in range(COL_NUM):
            if board[indices[y, x]].rune == Runes.EMPTY.value:
                print(f'\033[0m ', end=' ')
                continue
            color = Runes.int2color_code(board[indices[y, x]].rune)
            if board[indices[y, x]].rune == Runes.UNKNOWN.value or board[indices[y, x]].rune == Runes.HIDDEN.value:
                print(f'\033[1m{color}?', end=' ')
            else:
                symbol = '●' if board[indices[y, x]].untouchable == 0 else 'X'
                print(f'\033[1m{color}{symbol}', end=' ')
        print('\033[0m|')
    print('')


def print_two_board(board: list[Rune], indices: np.ndarray|None = None, indices2: np.ndarray|None = None) -> None:
    
        if indices is None:
            indices = np.array([[x + y * COL_NUM for x in range(COL_NUM)] for y in range(ROW_NUM)])
        if indices2 is None:
            indices2 = np.array([[x + y * COL_NUM for x in range(COL_NUM)] for y in range(ROW_NUM)])
        if indices is not None:
            assert indices.shape == (ROW_NUM, COL_NUM), 'invalid indices shape'
        if indices2 is not None:
            assert indices2.shape == (ROW_NUM, COL_NUM), 'invalid indices2 shape'
        
        # print('')
        for y in range(ROW_NUM):
            print('\033[0m|', end=' ')
            for x in range(COL_NUM):
                if board[indices[y, x]].rune == Runes.EMPTY.value:
                    print(f'\033[0m ', end=' ')
                    continue
                color = Runes.int2color_code(board[indices[y, x]].rune)
                if board[indices[y, x]].rune == Runes.UNKNOWN.value or board[indices[y, x]].rune == Runes.HIDDEN.value:
                    print(f'\033[1m{color}?', end=' ')
                else:
                    symbol = '●' if board[indices[y, x]].untouchable == 0 else 'X'
                    print(f'\033[1m{color}{symbol}', end=' ')
            print('\033[0m|', end='')
    
            if y == ROW_NUM // 2:
                print('  ->  ', end='')
            else:
                print('      ', end='')
    
            print('\033[0m|', end=' ')
            for x in range(COL_NUM):
                if board[indices2[y, x]].rune == Runes.EMPTY.value:
                    print(f'\033[0m ', end=' ')
                    continue
                color = Runes.int2color_code(board[indices2[y, x]].rune)
                if board[indices2[y, x]].rune == Runes.UNKNOWN.value or board[indices2[y, x]].rune == Runes.HIDDEN.value:
                    print(f'\033[1m{color}?', end=' ')
                else:
                    symbol = '●' if board[indices2[y, x]].untouchable == 0 else 'X'
                    print(f'\033[1m{color}{symbol}', end=' ')
            print('\033[0m|')
        # print('')


def get_adb_device() -> AdbDevice:
    devices: list[AdbDevice]
    try:
        adb = Client(host='127.0.0.1', port=5037)
        devices = adb.devices()
    except RuntimeError:
        print('ADB server not running, retrying...')
        os.system('adb devices')
        time.sleep(2)
        adb = Client(host='127.0.0.1', port=5037)
        devices = adb.devices()
        
    if len(devices) == 0:
        print('Devices not found')
        quit()
    print(f'{devices=}')
    
    return devices[0]


def race_str2int(race_str: str) -> int:
    if race_str == 'GOD' or race_str == '神': return 1
    if race_str == 'DEVIL' or race_str == '魔': return 2
    if race_str == 'HUMAN' or race_str == '人': return 3
    if race_str == 'ORC' or race_str == '獸': return 4
    if race_str == 'DRAGON' or race_str == '龍': return 5
    if race_str == 'ELF' or race_str == '妖': return 6
    if race_str == 'MECH' or race_str == '機': return 7
    if race_str == '': return 0
    # return 0
    raise ValueError(f'Invalid Race str')
