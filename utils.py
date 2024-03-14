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
    new_board_indices = board_indices.copy()
    for x in range(NUM_COL):
        new_col = []
        for y in range(NUM_ROW):
            if board_indices[y, x] != NUM_COL * NUM_ROW:
                new_col.append(board_indices[y, x])
        new_col = [NUM_COL * NUM_ROW] * (NUM_ROW - len(new_col)) + new_col
        new_board_indices[:, x] = new_col
    return new_board_indices


def eliminate_once_with_indices(board: list[Rune], board_indices: np.ndarray) -> tuple[int, int]:
    # print('Eliminating...')
    # print_board(board, board_indices)
    """
    board: a 1D list of Rune objects, end with a NONE_RUNE
    board_indices: a 2D numpy array of integers, representing the indices of the board
    """
    to_eliminate = np.zeros((NUM_ROW, NUM_COL), dtype=int)
    for y in range(NUM_ROW):
        for x in range(NUM_COL-2):
            # print(f'{y=}, {x=}, {board[board_indices[y, x]]=}')
            rune = board[board_indices[y, x]].rune
            if rune == board[board_indices[y, x+1]].rune and rune == board[board_indices[y, x+2]].rune:
                to_eliminate[y, x] = to_eliminate[y, x+1] = to_eliminate[y, x+2] = rune
    # to_eliminate = to_eliminate.astype(int)
    for i in range(NUM_ROW-2):
        for j in range(NUM_COL):
            rune = board[board_indices[i, j]].rune
            if rune == board[board_indices[i+1, j]].rune and rune == board[board_indices[i+2, j]].rune:
                to_eliminate[i, j] = to_eliminate[i+1, j] = to_eliminate[i+2, j] = rune
    # to_eliminate = to_eliminate.astype(int)
    # print('', to_eliminate, '', sep='\n')
    combo = 0
    total_eliminated = 0

    
    isZero = False
    idx = (0, 0)
    target = 0
    last_y = 0
    while not isZero:
        isZero = True
        for y in range(last_y, NUM_ROW):
            for x in range(NUM_COL):
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
            if y < NUM_ROW-1 and to_eliminate[y+1, x] and board[board_indices[y+1, x]].rune == target:
                stack.append((y+1, x))
            if x > 0 and to_eliminate[y, x-1] and board[board_indices[y, x-1]].rune == target:
                stack.append((y, x-1))
            if x < NUM_COL-1 and to_eliminate[y, x+1] and board[board_indices[y, x+1]].rune == target:
                stack.append((y, x+1))

        for y, x in visited:
            to_eliminate[y, x] = False
            board_indices[y, x] = NUM_COL * NUM_ROW
            total_eliminated += 1
    # print(f'{combo=}, {total_eliminated=}\n')
    # print_board(board, board_indices)

    return combo, total_eliminated
            

def evaluate_with_indices(board: list[Rune], board_indices: np.ndarray|None = None) -> tuple[int, int, int]:
    """
    Evaluate the board with the indices of the board.
    """
    if board_indices is None:
        board_indices = np.reshape(np.arange(NUM_COL * NUM_ROW), (NUM_ROW, NUM_COL))
    
    combo, total_eliminated = eliminate_once_with_indices(board, board_indices)
    board_indices = drop_indices(board_indices)
    
    if combo == 0:
        return 0, 0, 0
    
    f_c = combo
    c = 0
    eli = 0

    while combo > 0:
        c += combo
        eli += total_eliminated
        combo, total_eliminated = eliminate_once_with_indices(board, board_indices)
        board_indices = drop_indices(board_indices)

    return f_c, c, eli

def print_board(board: list[Rune], indices: np.ndarray|None = None) -> None:

    if indices is None:
        indices = np.array([[x + y * NUM_COL for x in range(NUM_COL)] for y in range(NUM_ROW)])
    if indices is not None:
        assert indices.shape == (NUM_ROW, NUM_COL), 'invalid indices shape'
    
    # print('')
    for y in range(NUM_ROW):
        print('\033[0m|', end=' ')
        for x in range(NUM_COL):
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
            indices = np.array([[x + y * NUM_COL for x in range(NUM_COL)] for y in range(NUM_ROW)])
        if indices2 is None:
            indices2 = np.array([[x + y * NUM_COL for x in range(NUM_COL)] for y in range(NUM_ROW)])
        if indices is not None:
            assert indices.shape == (NUM_ROW, NUM_COL), 'invalid indices shape'
        if indices2 is not None:
            assert indices2.shape == (NUM_ROW, NUM_COL), 'invalid indices2 shape'
        
        # print('')
        for y in range(NUM_ROW):
            print('\033[0m|', end=' ')
            for x in range(NUM_COL):
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
    
            if y == NUM_ROW // 2:
                print('  ->  ', end='')
            else:
                print('      ', end='')
    
            print('\033[0m|', end=' ')
            for x in range(NUM_COL):
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
