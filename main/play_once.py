import time

from ppadb.device import Device as AdbDevice

from routing.route_planning import get_indices_from_route, route_planning_c
# from routing.route_planning_c import route_planning_c
from tosgame.Runes import Runes
from util.events import AdbEventController
from util.read_board import read_board
from util.utils import get_adb_device, print_two_board, get_args_from_complexity, Complexity



# def play_once(device: AdbDevice|None=None, screenshot:MatLike|None=None, complexity: Complexity="Mid", read_effect: bool=False) -> None:

#     controller = AdbEventController(device)

#     # iter, max_first_depth, max_depth = get_args_from_complexity(complexity)
#     args = get_args_from_complexity(complexity)

#     if device is None:
#         device = get_adb_device()
    
#     if screenshot is None:
#         game = read_board(device=device, read_effect=read_effect)
#     else:
#         game = read_board(screenshot=screenshot, read_effect=read_effect)

#     indices = get_indices_from_route()

#     # return if there are unknown runes
#     if not all([game.board[indices[i, j]].rune != Runes.UNKNOWN.value for i in range(5) for j in range(6)]):
#         game.print_board()
#         print('\033[7F')
#         return
    
#     start_time = time.time()
        
#     # final_route = route_planning_c(game, iter, max_first_depth, max_depth, False)
#     final_route = route_planning_c(game, *args, False)
#     game_before_move = read_board(device, read_effect=read_effect)

#     print(f"route_planning_c took : {time.time() - start_time:.2f}s")

#     if (game_before_move == game):
#         indices = get_indices_from_route(final_route)
#         print_two_board(game.board, None, indices)
#         print(f'len: {len(final_route)}')
#         # route_move(device, final_route)
#         controller.route_move_no_root(final_route)
#         return
#     else:
#         print('board changed before move')


class GamePlayer:

    def __init__(self, device: AdbDevice|None=None, complexity: Complexity="Mid", read_effect: bool=False, debug: bool = False) -> None:
        if device is None:
            self.device = get_adb_device()
        else:
            self.device = device

        self.complexity = complexity
        self.read_effect = read_effect
        self.adb_controller = AdbEventController(device)
        self.debug = debug

        
    def play_once(self) -> None:
        args = get_args_from_complexity(self.complexity)
        game = read_board(device=self.device, read_effect=self.read_effect)

        # return if there are unknown runes
        if not all([game.board[i].rune != Runes.UNKNOWN.value for i in range(30)]):
            game.print_board()
            print('\033[7F')
            return
        
        if self.debug:
            start_time = time.time()
            
        final_route = route_planning_c(game, *args, False)
        game_before_move = read_board(self.device, read_effect=self.read_effect)

        if self.debug:
            print(f"route_planning_c took : {time.time() - start_time:.2f}s")

        if (game_before_move == game):
            indices = get_indices_from_route(final_route)
            print_two_board(game.board, None, indices)
            print(f'len: {len(final_route)}')
            self.adb_controller.route_move_no_root(final_route)
            return
        else:
            print('board changed before move')

    def set_complexity(self, complexity: Complexity) -> None:
        self.complexity = complexity
    

if __name__ == "__main__":

    game_player = GamePlayer(complexity="Mid", read_effect=False, debug=True)
    game_player.play_once()

    time.sleep(15)
    game_player.set_complexity("High")
    game_player.play_once()




    