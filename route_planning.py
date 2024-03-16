import numpy as np
from multiprocessing import Pool
from TosGame import TosGame
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


def get_runeboard_from_indices(board: list[Rune], board_indices: np.ndarray) -> np.ndarray:
    """
    Get a rune board of int of ndarray from a list of Rune objects and a 2D numpy array of indices.
    """
    new_board = np.zeros((NUM_ROW, NUM_COL), dtype=Rune)
    for y in range(NUM_ROW):
        for x in range(NUM_COL):
            new_board[y, x] = board[board_indices[y, x]]
    return new_board


def get_unconnected_count(rune_board: np.ndarray) -> int:
    """
    Get the number of unconnected runes in the board.
    """
    unconnected_count = 0
    for y in range(NUM_ROW):
        for x in range(NUM_COL):
            if rune_board[y, x].rune != 0:
                if y > 0 and rune_board[y-1, x].rune == rune_board[y, x].rune:
                    continue
                if y < NUM_ROW - 1 and rune_board[y+1, x].rune == rune_board[y, x].rune:
                    continue
                if x > 0 and rune_board[y, x-1].rune == rune_board[y, x].rune:
                    continue
                if x < NUM_COL - 1 and rune_board[y, x+1].rune == rune_board[y, x].rune:
                    continue
                unconnected_count += 1
    return unconnected_count

def dfs_cluster(rune_board: np.ndarray, visited: np.ndarray, position: tuple[int, int]) -> None:
    """
    Depth-first search to find the cluster of a rune.
    """
    x, y = position
    if visited[y, x]:
        return
    visited[y, x] = True
    if y > 0 and rune_board[y-1, x].rune == rune_board[y, x].rune:
        dfs_cluster(rune_board, visited, (x, y-1))
    if y < NUM_ROW - 1 and rune_board[y+1, x].rune == rune_board[y, x].rune:
        dfs_cluster(rune_board, visited, (x, y+1))
    if x > 0 and rune_board[y, x-1].rune == rune_board[y, x].rune:
        dfs_cluster(rune_board, visited, (x-1, y))
    if x < NUM_COL - 1 and rune_board[y, x+1].rune == rune_board[y, x].rune:
        dfs_cluster(rune_board, visited, (x+1, y))

def get_cluster_count(rune_board: np.ndarray) -> int:
    """
    Get the number of clusters in the board.
    """
    cluster_count = 0
    visited = np.zeros((NUM_ROW, NUM_COL), dtype=bool)
    for y in range(NUM_ROW):
        for x in range(NUM_COL):
            if not visited[y, x]:
                cluster_count += 1
                dfs_cluster(rune_board, visited, (x, y))
    return cluster_count


def get_board_score2(board: list[Rune], board_indices: np.ndarray, current_pos: tuple) -> float:
    
    # rune_board = get_runeboard_from_indices(board, board_indices)
    # unconnected_count = get_unconnected_count(rune_board)
    # cluster_count = get_cluster_count(rune_board)
    # return (30 - unconnected_count) * 10
    new_indices = board_indices.copy()
    f_c, c, eli, indices_first = evaluate_with_indices(board, new_indices)
    if indices_first[current_pos[1], current_pos[0]] == NUM_COL * NUM_ROW:
        return -1
    score = f_c * 100 + c * 20 + eli * 1
    
    IDX_EMPTY = NUM_COL * NUM_ROW
    
    for x in range(NUM_COL):
        score += 10 * (indices_first[0, x] == NUM_COL * NUM_ROW)
        score += 10 * (indices_first[NUM_ROW - 1, x] == NUM_COL * NUM_ROW)

    for y in range(NUM_ROW):
        score += 10 * (indices_first[y, 0] == NUM_COL * NUM_ROW)
        score += 10 * (indices_first[y, NUM_COL - 1] == NUM_COL * NUM_ROW)

    return score

def is_valid_move(x: int, y: int) -> bool:
    return 0 <= x < NUM_COL and 0 <= y < NUM_ROW

def get_next_board_indices(current_board_indices: np.ndarray, current_position: tuple, next_position: tuple) -> np.ndarray:

    new_board_indices = np.copy(current_board_indices)
    new_board_indices[current_position[1], current_position[0]] = current_board_indices[next_position[1], next_position[0]]
    new_board_indices[next_position[1], next_position[0]] = current_board_indices[current_position[1], current_position[0]]
    
    return new_board_indices

def dfs(board: TosGame, current_position: tuple, current_route: list[tuple[int, int]], current_board_indices: np.ndarray|None= None, max_depth: int=MAX_DEPTH) -> tuple[float, list[tuple[int, int]]]:
    if current_board_indices is None:
        current_board_indices = np.reshape(np.arange(NUM_COL * NUM_ROW), (NUM_ROW, NUM_COL))
    if len(current_route) > max_depth:
        return get_board_score2(board.board, current_board_indices, current_position), current_route

    best_score = float('-inf')
    best_route = []

    for move in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:  # Represents left, right, up, down, stop
    # for move in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
        if move == (0, 0):
            score, route = get_board_score2(board.board, current_board_indices, current_position), current_route
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
def maximize_score(board: TosGame, max_depth: int=MAX_DEPTH):
    assert isinstance(board, TosGame)
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

def maximize_score_parallel(board: TosGame, max_depth: int=MAX_DEPTH):
    assert isinstance(board, TosGame)
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
def route_planning(board: TosGame, iter: int, max_first_depth: int=8, max_depth: int=10, log_time: bool = False) -> tuple[int, list[tuple[int, int]]]:
    """
    Given a board, return the best score and best route.
    """
    assert isinstance(board, TosGame)

    final_route: list[tuple[int, int]] = []
    max_score = -1
    if log_time:
        time_start = time.time()
    if max_first_depth > 5:
        score, route = maximize_score_parallel(board, max_depth=max_first_depth)
    else:
        score, route = maximize_score(board, max_depth=max_first_depth)
    if log_time:
        print(f'First depth: {time.time() - time_start:.2f}s')
        time_start = time.time()
        max_iter = iter
    
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

    if log_time:
        print(f'Iter: {time.time() - time_start:.2f}s / {max_iter - iter} iters, avg: {(time.time() - time_start) / (max_iter - iter):.2f}s/iter')

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
    # device = get_adb_device()
    read_templates()

    iter = 30
    # max_first_depth = 9
    # max_depth = 12
    max_first_depth = 4
    max_depth = 5

    # board = read_board(device)
    board = read_board(None, 'E:/screenshot2.png')
    BOARD_FOR_ROUTE = board.board
    board.print_board()

    # first_combo, combo, totol_eliminated = evaluate_board(board.board, NUM_COL, NUM_ROW)
    # print(f'{first_combo=}, {combo=}, {totol_eliminated=}')

    # board.print_board()
    # test_board(board.board)
    # score, route = maximize_score(board, max_depth)
    score, route = route_planning(board, iter, max_first_depth, max_depth, True)
    indices = get_indices_from_route(route)

    print_two_board(board.board, None, indices)
    print(f'{score=}, len: {len(route)}')

    # get_board_score2(board.board, indices)

    f_c, c, eli, indices_first = evaluate_with_indices(board.board, indices)
    print(f'{f_c=}, {c=}, {eli=}')
    # print_board(board.board, indices_first)

    
    # board.print_board()

if __name__ == "__main__":
    main()


