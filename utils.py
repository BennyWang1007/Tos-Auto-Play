import os
import time
import psutil
import numpy as np

from MoveDir import MoveDir
from Runes import Runes
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
    raise 'invalid direction'


def int2MoveDir(dir: int) -> MoveDir:
    """convert int to MoveDir"""
    for d in MoveDir:
        if d.value == dir:
            return d
    raise 'invalid direction'


def int2MoveDir_str(dir: int) -> str:
    """convert int to MoveDir string"""
    for d in MoveDir:
        if d.value == dir:
            return d.name
    raise 'invalid direction'


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f'{func.__name__} elapsed time: {elapsed}')
        return result
    return wrapper


def set_process_priority():
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)


def print_board(board: np.ndarray, untouchable: np.ndarray = None):
    if untouchable is None:
        untouchable = np.zeros_like(board)
    # print('')
    for i in range(board.shape[0]):
        print('\033[0m|', end=' ')
        for j in range(board.shape[1]):
            color = Runes.int2color_code(board[i, j])
            if board[i, j] == Runes.UNKNOWN.value or board[i, j] == Runes.HIDDEN.value:
                print(f'\033[1m{color}?', end=' ')
            else:
                symbol = '●' if untouchable[i, j] == 0 else 'X'
                print(f'\033[1m{color}{symbol}', end=' ')
        print('\033[0m|')


def print_two_board(board: np.ndarray, board2: np.ndarray, untouchable: np.ndarray = None, untouchable2: np.ndarray = None):

    if untouchable is None:
        untouchable = np.zeros_like(board)
    if untouchable2 is None:
        untouchable2 = np.zeros_like(board2)

    if board.shape != board2.shape:
        raise ValueError('boards have different shapes')
    
    # print('')
    for i in range(board.shape[0]):
        print('\033[0m|', end=' ')
        for j in range(board.shape[1]):
            if board[i, j] == Runes.UNKNOWN.value:
                print('\033[0m?', end=' ')
            else:
                color = Runes.int2color_code(board[i, j])
                symbol = '●' if untouchable[i, j] == 0 else 'X'
                print(f'\033[1m{color}{symbol}', end=' ')
        print('\033[0m|', end='')
        if i == board.shape[0] // 2:
            print('  ->  ', end='')
        else:
            print('      ', end='')

        print('\033[0m|', end=' ')
        for j in range(board2.shape[1]):
            if board2[i, j] == Runes.UNKNOWN.value:
                print('\033[0m?', end=' ')
            else:
                color = Runes.int2color_code(board2[i, j])
                symbol = '●' if untouchable2[i, j] == 0 else 'X'
                print(f'\033[1m{color}{symbol}', end=' ')
        print('\033[0m|')
    # print('')


def get_adb_device() -> AdbDevice:

    adb = Client(host='127.0.0.1', port=5037)
    devices: list[AdbDevice] = adb.devices()

    if len(devices) == 0:
        print('Devices not found')
        quit()
    print(f'{devices=}')
    
    return devices[0]
