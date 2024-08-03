import random
import sys
import time

import cv2
import numpy as np
from ppadb.device import Device as AdbDevice

from util.read_board import read_board
from routing.route_planning import *
from routing.route_planning_c import route_planning_c
from tosgame.MoveDir import MoveDir
from tosgame.Runes import Runes, Rune
from tosgame.TosGame import TosGame
from util.constant import *
from util.utils import *

from util.events import route_move

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

    cd_image = cv2.imread('templates/cd.png', IMREAD_MODE)
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
                game = read_board(device, read_effect=False)
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
            
        game_before_move = read_board(device, read_effect=False)
        if (game_before_move == game):
            indices = get_indices_from_route(final_route)
            print_two_board(game.board, None, indices)
            print(f'{score=}, len: {len(final_route)}')
            route_move(device, final_route)
            prev_game = game
        else:
            # print('board changed before move')
            prev_game = game_before_move

        time.sleep(3)



    