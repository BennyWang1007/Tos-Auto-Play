import numpy as np
from multiprocessing import Pool
from Board import Board
from Runes import Runes
from MoveDir import MoveDir
from utils import *
from read_board import read_templates, read_board

def move2int(move: tuple[int, int]) -> int:
    """
    Convert a move tuple to an integer of MoveDir enum.
    """
    if move == (-1, 0):
        return MoveDir.LEFT.value
    elif move == (1, 0):
        return MoveDir.RIGHT.value
    elif move == (0, -1):
        return MoveDir.UP.value
    elif move == (0, 1):
        return MoveDir.DOWN.value
    elif move == (0, 0):
        return MoveDir.NONE.value
    else:
        raise ValueError(f'Invalid move: {move}')
    
def board_moves(board: np.ndarray, route: list) -> tuple[np.ndarray, bool]:
    """
    Apply a route to a board and return the new board and a boolean indicating whether the route is valid.
    """
    for (x, y) in route:
        if board[y, x].untouchable:
            return board, False
    start_rune = board[route[0][1], route[0][0]]
    for i in range(1, len(route)):
        board[route[i - 1][1], route[i - 1][0]] = board[route[i][1], route[i][0]]
    board[route[-1][1], route[-1][0]] = start_rune
    return board, True


def get_board_score2(board: list[Rune], board_indices: np.ndarray) -> float:
    
    new_indices = board_indices.copy()
    f_c, c, eli = evaluate_with_indices(board, new_indices)
    score = f_c * 6 + c * 4 + eli * 1

    return score

def is_valid_move(x: int, y: int) -> bool:
    return 0 <= x < NUM_COL and 0 <= y < NUM_ROW

def get_next_board_indices(current_board_indices: np.ndarray, current_position: tuple, next_position: tuple) -> np.ndarray:

    new_board_indices = np.copy(current_board_indices)
    new_board_indices[current_position[1], current_position[0]] = current_board_indices[next_position[1], next_position[0]]
    new_board_indices[next_position[1], next_position[0]] = current_board_indices[current_position[1], current_position[0]]
    
    return new_board_indices

def dfs(board: Board, current_position: tuple, current_route: list[tuple[int, int]], current_board_indices: np.ndarray|None= None, max_depth: int=MAX_DEPTH) -> tuple[float, list[tuple[int, int]]]:
    if current_board_indices is None:
        current_board_indices = np.reshape(np.arange(NUM_COL * NUM_ROW), (NUM_ROW, NUM_COL))
    if len(current_route) > max_depth:
        return get_board_score2(board.board, current_board_indices), current_route

    best_score = float('-inf')
    best_route = []

    for move in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:  # Represents left, right, up, down, stop
        if move == (0, 0):
            score, route = get_board_score2(board.board, current_board_indices), current_route
            if score > best_score:
                best_score = score
                best_route = route
            elif score == best_score and len(route) < len(best_route):
                best_route = route
        else:
            new_x, new_y = current_position[0] + move[0], current_position[1] + move[1]
            if is_valid_move(new_x, new_y) and not board.board[current_board_indices[new_y, new_x]].untouchable:
                new_position = (new_x, new_y)
                if new_position not in current_route:
                    new_route = current_route + [new_position]
                    new_board_indices = get_next_board_indices(current_board_indices, current_position, new_position)
                    score, route = dfs(board, new_position, new_route, new_board_indices, max_depth)
                    if score > best_score:
                        best_score = score
                        best_route = route
                    elif score == best_score and len(route) < len(best_route):
                        best_route = route
    return best_score, best_route

# @timeit
def maximize_score(board: Board, max_depth: int=MAX_DEPTH):
    assert isinstance(board, Board)
    best_score = float('-inf')
    best_route = []

    for start_position in [(x, y) for x in range(NUM_COL) for y in range(NUM_ROW)]:
        score, route = dfs(board, start_position, [start_position], None, max_depth)
        if score > best_score:
            best_score = score
            best_route = route
    
    return best_score, best_route

def dfs_wrapper(args):
    return dfs(*args)

def maximize_score_parallel(board: Board, max_depth: int=MAX_DEPTH):
    assert isinstance(board, Board)
    best_score = float('-inf')
    best_route = []

    start_positions = [(x, y) for x in range(NUM_COL) for y in range(NUM_ROW)]
    args = [(board.copy(), start_position, [start_position], None, max_depth) for start_position in start_positions]

    with Pool() as pool:
        results = list(pool.map(dfs_wrapper, args))
    
    for score, route in results:
        if score > best_score:
            best_score = score
            best_route = route
    
    return best_score, best_route

@timeit
def route_planning(board: Board, iter: int, max_first_depth: int=8, max_depth: int=10) -> tuple[int, list[tuple[int, int]]]:
    """
    Given a board, return the best score and best route.
    """
    assert isinstance(board, Board)

    final_route: list[tuple[int, int]] = []
    max_score = -1
    if max_first_depth > 5:
        score, route = maximize_score_parallel(board, max_depth=max_first_depth)
    else:
        score, route = maximize_score(board, max_depth=max_first_depth)
    
    while iter > 0 and score > max_score:
        max_score = score
        if len(final_route) == 0:
            final_route = route
        else:
            final_route += route[1:]
        indices = get_indices_from_route(final_route)
        # board.board, success = board_moves(board.board, route)
        score, route = dfs(board, route[-1], [route[-1]], indices, max_depth)
        iter -= 1

    return max_score, final_route


def get_indices_from_route(route: list[tuple[int, int]]|None = None) -> np.ndarray:
    
    indices = np.reshape(np.arange(NUM_COL * NUM_ROW), (NUM_ROW, NUM_COL))
    if route is None or len(route) == 0:
        return indices
    start_rune = indices[route[0][1], route[0][0]]

    for i in range(1, len(route)):
        indices[route[i-1][1], route[i-1][0]] = indices[route[i][1], route[i][0]]
    indices[route[-1][1], route[-1][0]] = start_rune
    
    return indices

    
@timeit
def main():
    global BOARD_FOR_ROUTE
    device = get_adb_device()
    read_templates()

    iter = 5
    max_first_depth = 7
    max_depth = 9

    board = read_board(device)
    BOARD_FOR_ROUTE = board.board
    board.print_board()

    # first_combo, combo, totol_eliminated = evaluate_board(board.board, NUM_COL, NUM_ROW)
    # print(f'{first_combo=}, {combo=}, {totol_eliminated=}')

    # board.print_board()
    # test_board(board.board)
    # score, route = maximize_score(board, max_depth)
    score, route = route_planning(board, iter, max_first_depth, max_depth)
    indices = get_indices_from_route(route)

    print_two_board(board.board, None, indices)
    print(f'{score=}, len: {len(route)}')

    
    # board.print_board()

if __name__ == "__main__":
    main()


