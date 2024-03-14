import numpy as np
import utils
from utils import evaluate_with_indices, drop_indices, eliminate_once_with_indices
from MoveDir import MoveDir
from constant import FIXED_BOARD
from Runes import Runes, Rune
from copy import deepcopy

class Board:
    """A class of tos board"""

    offset = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def __init__(self, num_col=6, num_row=5, num_rune=6, max_move=30, num_action=9, mode='random', extra_obs=4) -> None:
        self.num_col = num_col
        self.num_row = num_row
        self.num_rune = num_rune
        self.board_size = num_col * num_row
        self.max_move = max_move
        self.num_action = num_action
        self.mode = mode
        self.extra_obs = extra_obs
        self.empty_rune = Rune(0, False, False)
        # self.board = [Rune(np.random.randint(1, 1+self.num_rune), False, False) for _ in range(self.num_row * self.num_col)] + [self.empty_rune]
        # self.indices = np.array([[x + y * self.num_col for x in range(self.num_col)] for y in range(self.num_row)])
        self.reset()

    def print_attr(self):
        print(f'{self.num_col=}, {self.num_row=}, {self.num_rune=}, {self.max_move=}, {self.num_action=}, {self.mode=}, {self.extra_obs=}')
        print(f'{self.cur_x=}, {self.cur_y=}')

    def set_board(self, board: list[Rune]) -> None:
        # assert board.shape == (self.num_row, self.num_col), f'invalid board shape: {board.shape}'
        # assert isinstance(board[0][0], Rune), f'invalid board type: {type(board[0][0])}'
        self.board = board

    def set_cur_pos(self, x: int, y: int) -> None:
        self.cur_x = x
        self.cur_y = y

    def set_by_obs(self, obs: np.ndarray) -> None:
        pass
        # self.board = obs[:self.num_col*self.num_row].reshape((self.num_row, self.num_col))
        # self.cur_x = obs[self.num_col*self.num_row]
        # self.cur_y = obs[self.num_col*self.num_row+1]
        # self.prev_action = obs[self.num_col*self.num_row+2]
        # if len(obs) > self.num_col*self.num_row+3:
        #     self.move_count = self.max_move - obs[self.num_col*self.num_row+3]

    def reset_combo(self):
        self.combo = 0
        self.first_combo = 0
        self.totol_eliminated = 0

    def reset(self):
        self.reset_combo()
        self.move_count = 0
        self.cur_x = 0
        self.cur_y = 0
        self.action_invalid = False
        self.action = -1
        self.prev_action = -1
        self.terminate = False
        # if mode is fixed and fixed board exists, use fixed board
        if self.mode == 'fixed' and (self.num_col, self.num_row) in FIXED_BOARD:
            raise NotImplementedError
            self.board = FIXED_BOARD[(self.num_col, self.num_row)].copy()
        else:
            while True:
                # self.board = np.random.randint(1, 1+self.num_rune, (self.num_row, self.num_col))
                self.board = [Rune(np.random.randint(1, 1+self.num_rune), False, False) for _ in range(self.num_row * self.num_col)] + [self.empty_rune]
                self.indices = np.array([[x + y * self.num_col for x in range(self.num_col)] for y in range(self.num_row)])
                # print(id(self.board))
                self.evaluate()
                if self.first_combo == 0:
                    break
        self.reset_combo()

    def random_board(self):
        self.reset()

    def random_pos(self):
        self.cur_x = np.random.randint(0, self.num_col)
        self.cur_y = np.random.randint(0, self.num_row)
        self.move_count = 0

    def eliminate_once(self, is_first=False) -> None:
        # combo, totol_eliminated = evaluate_with_indices(self.board, self.indices)
        combo, totol_eliminated = eliminate_once_with_indices(self.board, self.indices)
        if is_first:
            self.first_combo += combo
        self.combo += combo
        self.totol_eliminated += totol_eliminated
        self.indices = drop_indices(self.indices)

    def eliminate(self):
        self.reset_combo()
        self.first_combo, self.combo, self.totol_eliminated = evaluate_with_indices(self.board, self.indices)
        
    def evaluate(self) -> None:
        """
        evaluate the board after elimination
        the board will not be modified
        """
        indices_copy = self.indices.copy()
        self.eliminate()
        self.indices = indices_copy

    def drop(self):
        # drop runes
        for i in range(self.num_col):
            stack = []
            for j in range(self.num_row):
                if self.board[j][i] != 0:
                    stack.append(self.board[j][i])
            if len(stack) < self.num_row:
                stack = [0] * (self.num_row - len(stack)) + stack
            for j in range(self.num_row):
                self.board[j][i] = stack[j]

    def move(self, action: int):
        '''move rune to the direction of dir'''

        self.action_invalid = False

        # set prev_action
        if self.action != -1:
            self.prev_action = self.action
        
        # invalid direction
        if action > self.num_action - 1: 
            print(f'invalid action: {action}, {self.num_action=}')
            self.action_invalid = True
            return
        
        # end move
        if action == MoveDir.NONE.value:
            self.terminate = True
            return
        
        self.move_count += 1
        x, y = self.cur_x, self.cur_y
        dx, dy = self.offset[action]
        next_x, next_y = x+dx, y+dy
        if next_x < 0 or next_x >= self.num_col or next_y < 0 or next_y >= self.num_row:
            self.action_invalid = True
            return
        self.cur_x = next_x
        self.cur_y = next_y
        # self.board[y][x], self.board[next_y][next_x] = self.board[next_y][next_x], self.board[y][x]
        self.indices[y, x], self.indices[next_y, next_x] = self.indices[next_y, next_x], self.indices[y, x]

        if not self.action_invalid:
            self.action = action

        # self.evaluate()

    def is_game_over(self):
        return self.terminate or self.move_count >= self.max_move

    def print_board(self):
        utils.print_board(self.board)

    # copy constructor
    def copy(self):
        new_board = Board(self.num_col, self.num_row, self.num_rune, self.max_move, self.num_action, self.mode, self.extra_obs)
        new_board.num_col = self.num_col
        new_board.num_row = self.num_row
        new_board.num_rune = self.num_rune
        new_board.max_move = self.max_move
        new_board.num_action = self.num_action
        new_board.mode = self.mode
        new_board.extra_obs = self.extra_obs
        new_board.board = deepcopy(self.board)
        new_board.cur_x = self.cur_x
        new_board.cur_y = self.cur_y
        new_board.move_count = self.move_count
        new_board.action_invalid = self.action_invalid
        new_board.action = self.action
        new_board.prev_action = self.prev_action
        new_board.terminate = self.terminate
        new_board.first_combo = self.first_combo
        new_board.combo = self.combo
        new_board.totol_eliminated = self.totol_eliminated
        # new_board.untouchable = self.untouchable.copy()
        # new_board.eliminable = self.eliminable.copy()
        # new_board.must_remove = self.must_remove.copy()

        return new_board
    
    def idx2pos(self, idx: int) -> tuple[int, int]:
        """convert index to x, y position"""
        return (idx % self.num_col, idx // self.num_col)

    def pos2idx(self, x: int, y: int) -> int:
        """convert position to index"""
        return y * self.num_col + x

# def get_board(obs: np.ndarray, num_col: int, num_row: int, num_rune: int, max_move: int, num_action: int) -> Board:
#     """get board from obs"""
#     board = Board(num_col, num_row, num_rune, max_move, num_action)
#     board.board = obs[:num_col*num_row].reshape((num_row, num_col))
#     board.cur_x = obs[num_col*num_row]
#     board.cur_y = obs[num_col*num_row+1]
#     board.prev_action = obs[num_col*num_row+2]
#     if len(obs) > num_col*num_row+3:
#         board.move_count = max_move - obs[num_col*num_row+3]
#     return board


# def eliminate_once(board: list[list[Rune]], num_col, num_row) -> tuple[int, int]:
#     """
#     Eliminate the board once, return the combo and total eliminated runes count
#     """
#     to_eliminate = np.zeros((num_row, num_col), dtype=int)
#     for x in range(num_col-2):
#         for y in range(num_row):
#             rune = board[y][x].rune
#             if rune < 1 or rune > 6: continue
#             if board[y][x+1].rune == rune and board[y][x+2].rune == rune:
#                 to_eliminate[y][x] = rune
#                 to_eliminate[y][x+1] = rune
#                 to_eliminate[y][x+2] = rune
            
#     for x in range(num_col):
#         for y in range(num_row-2):
#             rune = board[y][x].rune
#             if rune < 1 or rune > 6: continue
#             if board[y+1][x].rune == rune and board[y+2][x].rune == rune:
#                 to_eliminate[y][x] = rune
#                 to_eliminate[y+1][x] = rune
#                 to_eliminate[y+2][x] = rune

#     # print(f'to_eliminate:\n{to_eliminate}')

#     for x in range(num_col):
#         for y in range(num_row):
#             if to_eliminate[y][x] != 0:
#                 board[y][x].rune = 0
#                 board[y][x].untouchable = False
#                 board[y][x].must_remove = False

#     last_y = 0
#     target = 0
#     combo = 0
#     totol_eliminated = 0

#     while True:
#         isZero = True
#         for i in range(last_y, num_row):
#             for j in range(num_col):
#                 if to_eliminate[i][j] != 0:
#                     isZero = False
#                     last_y = i
#                     idx = (i, j)
#                     target = to_eliminate[i][j]
#                     break
#             if not isZero: break
#         if isZero: break
#         combo += 1
#         stack = [idx]
#         visited = []
#         while stack:
#             idx = stack.pop()
#             if idx in visited: continue
#             visited.append(idx)
#             if idx[0] > 0:
#                 if to_eliminate[idx[0]-1][idx[1]] == target:
#                     stack.append((idx[0]-1, idx[1]))
#             if idx[0] < num_row-1:
#                 if to_eliminate[idx[0]+1][idx[1]] == target:
#                     stack.append((idx[0]+1, idx[1]))
#             if idx[1] > 0:
#                 if to_eliminate[idx[0]][idx[1]-1] == target:
#                     stack.append((idx[0], idx[1]-1))
#             if idx[1] < num_col-1:
#                 if to_eliminate[idx[0]][idx[1]+1] == target:
#                     stack.append((idx[0], idx[1]+1))

#             to_eliminate[idx[0]][idx[1]] = 0
#             totol_eliminated += 1

#     return combo, totol_eliminated


# def drop_runes(board: list[list[Rune]], num_col, num_row):
#     for i in range(num_col):
#         stack = []
#         for j in range(num_row):
#             if board[j][i].rune != 0:
#                 stack.append(board[j][i])
#         if len(stack) < num_row:
#             stack = [Rune(0, False, False) for _ in range(num_row - len(stack))] + stack
#         for j in range(num_row):
#             board[j][i] = stack[j]


# def evaluate_board(board: np.ndarray, num_col: int, num_row: int):
#     """evaluate the board"""
#     isFisrt = True
#     newboard = deepcopy(board)

#     first_combo = 0
#     combo = 0
#     totol_eliminated = 0
#     while True:
#         combo_, eliminated = eliminate_once(newboard, num_col, num_row)
#         if combo_ == 0: break
#         if isFisrt:
#             first_combo += combo_
#         combo += combo_
#         totol_eliminated += eliminated
#         drop_runes(newboard, num_col, num_row)
#         isFisrt = False
    
#     return first_combo, combo, totol_eliminated



if __name__ == "__main__":
    board = Board()
    board.print_board()

    