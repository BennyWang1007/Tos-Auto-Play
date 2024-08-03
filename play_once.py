import random
import sys
import time

import cv2
import numpy as np
from typing import Literal
from ppadb.device import Device as AdbDevice

# from routing.route_planning import get_indices_from_route
# from routing.route_planning_c import route_planning_c
from tosgame.Runes import Runes
from tosgame.TosGame import TosGame
from util.read_board import read_board
from util.utils import get_adb_device, print_two_board
from util.constant import COL_NUM, ROW_NUM, GET_ROUTE_EXE_PATH

from util.events import route_move

"""-----------------to delete-----------------"""

def get_indices_from_route(route: list[tuple[int, int]]|None = None) -> np.ndarray:
    
    indices = np.reshape(np.arange(COL_NUM * ROW_NUM), (ROW_NUM, COL_NUM))
    if route is None or len(route) == 0:
        return indices
    start_rune = indices[route[0][1], route[0][0]]

    for i in range(1, len(route)):
        indices[route[i-1][1], route[i-1][0]] = indices[route[i][1], route[i][0]]
    indices[route[-1][1], route[-1][0]] = start_rune
    
    return indices

import subprocess

def route_planning_c(game: TosGame, iter: int, max_first_depth: int, max_depth: int, debug: bool) -> list[tuple[int, int]]:

    rune_str = game.rune_str()
    race_str = game.race_str()
    min_match_str = game.min_match_str()
    must_remove_str = game.must_remove_str()
    setting_str = game.setting_str()

    command = [
        GET_ROUTE_EXE_PATH , '-i', str(iter), '-f', str(max_first_depth), '-d', str(max_depth),
        '-rune', rune_str,'-race', race_str, '-min_match', min_match_str,
        '-must', must_remove_str, '-setting', setting_str
    ]
    # print(f"{command=}\n")
    # Execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if the command was executed successfully
    if result.returncode == 0:
        # print("C++ program executed successfully")
        # print('stdout:\n', result.stdout)
        final_route_str = result.stdout
        final_route_str = final_route_str.replace("(", "").replace(")", "").replace("\n", "")
        final_route_list = final_route_str.split(", ")
        final_route = [(int(final_route_list[i]), int(final_route_list[i + 1])) for i in range(0, len(final_route_list), 2)]
        return final_route
    else:
        # If there was an error, print the error message from stderr
        print("Error executing the C++ program:")
        print(result.stderr)
        return []



"""-----------------to delete-----------------"""

def play_once(device: AdbDevice, complexity: Literal["Low", "Mid", "High", "Extreme"], read_effect: bool=False) -> TosGame:

    if complexity == "Low":
        iter = 20
        max_first_depth = 5
        max_depth = 6
    elif complexity == "Mid":
        iter = 25
        max_first_depth = 6
        max_depth = 7
    elif complexity == "High":
        iter = 30
        max_first_depth = 7
        max_depth = 9
    elif complexity == "Extreme":
        iter = 35
        max_first_depth = 8
        max_depth = 10
    else:
        raise ValueError(f"Invalid complexity: {complexity}")
    
    # read board until no unknown runes
    while True:
        # if cd is found, then read board
        game = read_board(device, read_effect=read_effect)
        indices = get_indices_from_route()
        if all([game.board[indices[i, j]].rune != Runes.UNKNOWN.value for i in range(5) for j in range(6)]):
            break
        game.print_board()
        print('\033[7F')
        
        time.sleep(1)

    final_route = route_planning_c(game, iter, max_first_depth, max_depth, False)
    game_before_move = read_board(device, read_effect=read_effect)

    if (game_before_move == game):
        indices = get_indices_from_route(final_route)
        print_two_board(game.board, None, indices)
        print(f'len: {len(final_route)}')
        route_move(device, final_route)
        return game
    else:
        print('board changed before move')
        time.sleep(1)
        return play_once(device, complexity)
    

if __name__ == "__main__":
        
    device = get_adb_device()
    play_once(device, "Low", read_effect=False)




    