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
from route_planning_c import route_planning_c


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
ABS_MT_TRACKING_ID = 58
DEV = '/dev/input/event2'

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

def route_move(device: AdbDevice, route: list[tuple[int, int]]) -> None:
    route_loc = [get_grid_loc(x, y) for x, y in route]
    tolerance = RUNE_SIZE // 4
    dx, dy = random.randint(-tolerance, tolerance), random.randint(-tolerance, tolerance)
    route_loc = [(x + RUNE_SIZE // 2 + dx, y + RUNE_SIZE // 2 + dy) for x, y in route_loc]
    route_loc = [(y, SCREEN_WIDTH - x) for x, y in route_loc] # weird coordinate system of ld player

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

    iter = 30
    max_first_depth = 7
    max_depth = 9

    prev_game = None
    execute_times = 0
    score = 0
    final_route = []

    cd_image = cv2.imread('image/cd.png', IMREAD_MODE)
    h, w = cd_image.shape[:2]
    h, w = int(h * SCREEN_WIDTH / 1080.), int(w * SCREEN_HEIGHT / 1920.)
    cd_image = cv2.resize(cd_image, (w, h), interpolation=cv2.INTER_AREA)
    cd_mask = cd_image[:, :, 3]
    cd_image = cd_image[:, :, :3]
    
    while True:
        # read board until no unknown runes
        while True:
            pic = device.screencap()
            screenshot = cv2.imdecode(np.frombuffer(pic, np.uint8), IMREAD_MODE)
            screenshot = screenshot[:, :, :3]
            res = cv2.matchTemplate(screenshot, cd_image, cv2.TM_CCOEFF_NORMED, mask=cd_mask)

            threshold = np.array([0.8])
            loc = np.where(res >= threshold)

            # if cd is found, then read board
            if len(loc[0]) > 0:
                game = read_board(device)
                indices = get_indices_from_route()
                if all([game.board[indices[i, j]].rune != Runes.UNKNOWN.value for i in range(5) for j in range(6)]):
                    break
                game.print_board()
                print('\033[7F')
            else:
                pass
                # print('CD not found, max = ', res.max())
            time.sleep(1)

        same_board = (game == prev_game)

        if not same_board:
            execute_times += 1
            game.print_board()
            if execute_times > run_times:
                print('\033[7F\033[J')
                break

        if not same_board:
            # score, final_route = route_planning(game, iter, max_first_depth, max_depth, True)
            final_route = route_planning_c(game, iter, max_first_depth, max_depth, False)
            indices = get_indices_from_route(final_route)
            print_two_board(game.board, None, indices)
            print(f'{score=}, len: {len(final_route)}')

        game_before_move = read_board(device)
        if (game_before_move == game):
            route_move(device, final_route)
            prev_game = game
        else:
            # print('board changed before move')
            prev_game = game_before_move

        time.sleep(3)



    