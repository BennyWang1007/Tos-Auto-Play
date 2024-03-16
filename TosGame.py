import numpy as np
import utils
from utils import evaluate_with_indices, drop_indices, eliminate_once_with_indices
from MoveDir import MoveDir
from constant import FIXED_BOARD
from Runes import Runes, Rune
from copy import deepcopy

class TosGame:
    """A class of tos board"""

    offset = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def __init__(self, num_col=6, num_row=5, num_rune=6, mode='random') -> None:
        self.num_col = num_col
        self.num_row = num_row
        self.num_rune = num_rune
        self.board_size = num_col * num_row
        self.mode = mode
        self.empty_rune = Rune(0, False, False)
        self.reset()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TosGame): return False
        if len(self.board) != len(o.board): return False
        for i in range(len(self.board)):
            if self.board[i] != o.board[i]:
                return False
        return True

    def __repr__(self) -> str:
        return f'TosGame({self.num_col=}, {self.num_row=}, {self.board=}'

    def set_board(self, board: list[Rune]) -> None:
        assert len(board) == self.num_col * self.num_row + 1
        self.board = board

    def set_cur_pos(self, x: int, y: int) -> None:
        self.cur_x = x
        self.cur_y = y

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
        # use fixed board if it exists, otherwise random board
        if self.mode == 'fixed' and (self.num_col, self.num_row) in FIXED_BOARD:
            self.board = FIXED_BOARD[(self.num_col, self.num_row)].copy()
        else:
            while True:
                self.board = [Rune(np.random.randint(1, 1+self.num_rune), False, False) for _ in range(self.num_row * self.num_col)] + [self.empty_rune]
                self.indices = np.array([[x + y * self.num_col for x in range(self.num_col)] for y in range(self.num_row)])
                self.evaluate()
                if self.first_combo == 0: break
        self.reset_combo()

    def __str__(self) -> str:
        s = ""
        for idx in range(self.num_row * self.num_col):
            if self.board[idx].rune == Runes.WATER.value:
                s += 'W'
            elif self.board[idx].rune == Runes.FIRE.value:
                s += 'F'
            elif self.board[idx].rune == Runes.WOOD.value:
                s += 'E'
            elif self.board[idx].rune == Runes.LIGHT.value:
                s += 'L'
            elif self.board[idx].rune == Runes.DARK.value:
                s += 'D'
            elif self.board[idx].rune == Runes.HEART.value:
                s += 'H'
            else:
                s += '?'
            if (idx+1) % self.num_col == 0:
                s += '\n'
            else:
                s += ' '
        return s


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
        self.first_combo, self.combo, self.totol_eliminated, self.indices_after_first_elimination = evaluate_with_indices(self.board, self.indices)
        
    def evaluate(self) -> None:
        """
        evaluate the board after elimination
        the board will not be modified
        """
        indices_copy = self.indices.copy()
        self.eliminate()
        self.indices = indices_copy

    def drop(self):
        self.indices = drop_indices(self.indices)

    def move(self, action: int):
        '''move rune to the direction of dir'''

        self.action_invalid = False

        # set prev_action
        if self.action != -1:
            self.prev_action = self.action
        
        # end move
        if action == MoveDir.NONE.value:
            return
        
        self.move_count += 1
        x, y = self.cur_x, self.cur_y
        dx, dy = self.offset[action]
        next_x, next_y = x + dx, y + dy
        if next_x < 0 or next_x >= self.num_col or next_y < 0 or next_y >= self.num_row:
            self.action_invalid = True
            return
        self.cur_x = next_x
        self.cur_y = next_y
        self.indices[y, x], self.indices[next_y, next_x] = self.indices[next_y, next_x], self.indices[y, x]

        if not self.action_invalid:
            self.action = action

        # self.evaluate()

    def print_board(self):
        utils.print_board(self.board)

    # copy constructor
    def copy(self):
        new_board = TosGame(self.num_col, self.num_row, self.num_rune, self.mode)
        new_board.num_col = self.num_col
        new_board.num_row = self.num_row
        new_board.num_rune = self.num_rune
        new_board.mode = self.mode
        new_board.board = deepcopy(self.board)
        new_board.cur_x = self.cur_x
        new_board.cur_y = self.cur_y
        new_board.move_count = self.move_count
        new_board.action_invalid = self.action_invalid
        new_board.action = self.action
        new_board.prev_action = self.prev_action
        new_board.first_combo = self.first_combo
        new_board.combo = self.combo
        new_board.totol_eliminated = self.totol_eliminated

        return new_board


if __name__ == "__main__":
    board = TosGame()
    board.print_board()

    