import cv2
import random
import numpy as np
import time
from ppadb.device import Device as AdbDevice
from Board import Board
from Runes import Runes
from MoveDir import MoveDir
from route_planning import maximize_score, maximize_score_parallel, move2int, dfs, board_moves
from utils import *
from constant import *
from read_board import read_templates, read_board


"""-----------------send event functions-----------------"""

EV_SYN = 0
EV_KEY = 1
EV_ABS = 3

SYN_REPORT = 0
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
# ABS_MT_TRACKING_ID = 57
ABS_MT_TRACKING_ID = 58
BTN_TOUCH = 330

DEV = '/dev/input/event1'

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
    # route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc] # weird coordinate system of simulator

    send_ABS_MT_TRACKING_ID(device, 1)
    sendevent(device, EV_KEY, BTN_TOUCH, 1)

    for x, y in route_loc:
        send_POSITION(device, x, y)

    send_ABS_MT_TRACKING_ID(device, -1)
    sendevent(device, EV_KEY, BTN_TOUCH, 0)
    send_SYN_REPORT(device)

@timeit
def route_planning(board: Board, iter: int, max_first_depth: int=8, max_depth: int=10) -> tuple[int, list[tuple[int, int]]]:
    assert isinstance(board, Board)
    """
    Given a board, return the best score and best route.
    """
    final_route = []
    max_score = -1
    if max_first_depth > 7:
        score, route = maximize_score_parallel(board, max_depth=max_first_depth)
    else:
        score, route = maximize_score(board, max_depth=max_first_depth)
    
    while iter > 0 and score > max_score:
        max_score = score
        if len(final_route) == 0:
            final_route = route
        else:
            final_route += route[1:]
        board.board = board_moves(board.board, route)
        score, route = dfs(board, route[-1], [route[-1]], max_depth)
        iter -= 1

    return max_score, final_route


if __name__ == "__main__":

    device = get_adb_device()
    read_templates()
    
    iter = 5
    max_first_depth = 6
    max_depth = 9
    
    # main loop
    while True:

        # read board until no unknown runes
        while True:
            board = read_board(device)
            if np.sum(board.board == Runes.UNKNOWN.value) == 0:
                break
            board.print_board()
            time.sleep(1)

        score, final_route = route_planning(board.copy(), iter, max_first_depth, max_depth)

        # move the board to display the result
        board_copy = board.board.copy()
        board.cur_x, board.cur_y = final_route[0][0], final_route[0][1]
        for i in range(1, len(final_route)):
            dx, dy = final_route[i][0] - final_route[i - 1][0], final_route[i][1] - final_route[i - 1][1]
            board.move(move2int((dx, dy)))
        
        print_two_board(board_copy, board.board)
        print(f'{score=}, len: {len(final_route)}')

        route_move(device, final_route)
        time.sleep(3)


    