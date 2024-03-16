import random
import numpy as np
import time
import sys
from ppadb.device import Device as AdbDevice
from TosGame import TosGame
from Runes import Runes
from MoveDir import MoveDir
from route_planning import *
from utils import *
from constant import *
from read_board import read_templates, read_board


"""-----------------send event constant and functions-----------------"""

# suitable for Asus Zenfone M2
EV_SYN = 0
EV_KEY = 1
EV_ABS = 3

SYN_REPORT = 0
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
BTN_TOUCH = 330

DEV = '/dev/input/event1'

# for ld player
# ABS_MT_TRACKING_ID = 58
# DEV = '/dev/input/event2'

def sendevent(device: AdbDevice,type: int, code: int, value: int, dev: str=DEV):
    device.shell(f'sendevent {dev} {type} {code} {value}')

def send_SYN_REPORT(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_SYN, SYN_REPORT, 0, dev)

def send_BTN_TOUCH_DOWN(device: AdbDevice, dev: str=DEV) -> None:
    sendevent(device, EV_KEY, BTN_TOUCH, 1, dev)

def send_POSITION(device: AdbDevice, x: int, y: int, dev: str=DEV) -> None:
    sendevent(device, EV_ABS, ABS_MT_POSITION_X, x, dev)
    sendevent(device, EV_ABS, ABS_MT_POSITION_Y, y, dev)
    send_SYN_REPORT(device, dev)

def send_ABS_MT_TRACKING_ID(device: AdbDevice, x: int, dev: str=DEV) -> None:
    sendevent(device, EV_ABS, ABS_MT_TRACKING_ID, x, dev)


"""-----------------send event functions-----------------"""

def route_move(device, route) -> None:
    route_loc = [get_grid_loc(x, y) for x, y in route]
    tolerance = RUNE_SIZE // 4
    dx, dy = random.randint(-tolerance, tolerance), random.randint(-tolerance, tolerance)
    route_loc = [(x + RUNE_SIZE // 2 + dx, y + RUNE_SIZE // 2 + dy) for x, y in route_loc]
    # route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc] # weird coordinate system of ld player

    send_ABS_MT_TRACKING_ID(device, 1)
    sendevent(device, EV_KEY, BTN_TOUCH, 1)

    for x, y in route_loc:
        send_POSITION(device, x, y)

    send_ABS_MT_TRACKING_ID(device, -1)
    sendevent(device, EV_KEY, BTN_TOUCH, 0)
    send_SYN_REPORT(device)


if __name__ == "__main__":

    
    if len(sys.argv) > 1:
        run_times = int(sys.argv[1])
    else:
        run_times = 100
    
    device = get_adb_device()
    read_templates()
    
    # iter = 30
    # max_first_depth = 4
    # max_depth = 5
    iter = 30
    max_first_depth = 7
    max_depth = 10

    prev_board = None
    execute_times = 0
    score = 0
    final_route = []
    
    while True:
        # read board until no unknown runes
        while True:
            board = read_board(device)
            indices = get_indices_from_route()
            if all([board.board[indices[i, j]].rune != Runes.UNKNOWN.value for i in range(5) for j in range(6)]):
                break
            board.print_board()
            time.sleep(1)
            print('\033[8F')

        same_board = (board == prev_board)

        if not same_board:
            execute_times += 1
            board.print_board()
            if execute_times > run_times:
                print('\033[7F\033[J')
                break

        if not same_board:
            score, final_route = route_planning(board, iter, max_first_depth, max_depth, True)
            indices = get_indices_from_route(final_route)
            # print('\033[7F')
            print_two_board(board.board, None, indices)
            print(f'{score=}, len: {len(final_route)}')

        route_move(device, final_route)
        time.sleep(3)
        prev_board = board


    