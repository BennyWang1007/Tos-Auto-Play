import sys
import time

from routing.route_planning import route_planning_c, get_indices_from_route
# from routing.route_planning_c import route_planning_c
from tosgame.Runes import Runes
from util.constant import *
from util.events import AdbEventController
from util.read_board import read_board
from util.utils import *


if __name__ == "__main__":

    if len(sys.argv) > 1:
        run_times = int(sys.argv[1])
    else:
        run_times = 100
    
    device = get_adb_device()

    args = get_args_from_complexity("Mid")

    prev_game = None
    execute_times = 0
    score = 0
    final_route = []

    adb_controller = AdbEventController(device)
    
    while True:
        # read board until no unknown runes
        while True:
            screenshot = screencap(device)

            game = read_board(screenshot=screenshot, read_effect=False)
            indices = get_indices_from_route()
            if all([game.board[indices[i, j]].rune != Runes.UNKNOWN.value for i in range(5) for j in range(6)]):
                break
            game.print_board()
            print('\033[7F')

            time.sleep(5)

        same_board = (game == prev_game)

        if not same_board:
            execute_times += 1
            # game.print_board()
            if execute_times > run_times:
                print('\033[7F\033[J')
                break
            final_route = route_planning_c(game, *args, False)
            
        game_before_move = read_board(device, read_effect=True)
        if (game_before_move == game):
            indices = get_indices_from_route(final_route)
            print_two_board(game.board, None, indices)
            print(f'{score=}, len: {len(final_route)}')
            adb_controller.route_move_no_root(final_route)
            prev_game = game
        else:
            # print('board changed before move')
            prev_game = game_before_move

        time.sleep(5)



    