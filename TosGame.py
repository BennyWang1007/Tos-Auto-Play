import numpy as np
import utils
from utils import evaluate_with_indices, drop_indices, eliminate_once_with_indices, race_str2int
from MoveDir import MoveDir
from constant import FIXED_BOARD, SettingType
from Runes import Runes, Rune
from copy import deepcopy

def is_rune(str):
    return str in ['water', 'fire', 'grass', 'light', 'dark', 'heart']
    
def is_race(str):
    pass


class TosGame:
    """A class of tos board"""

    offset = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def __init__(self, num_col=6, num_row=5, num_rune=6, mode='random', *kwargs) -> None:

        self.has_setting = True
        # self.has_default_setting = False
        self.default_board_setting: SettingType = {
            'eli_color': [], # list of rune_str
            'min_match_color': [], # list of tuple (rune_str, num)
            'min_match_race': [], # list of tuple (race_str, num) such as ('神', 1)
            'no_first': [], # list of rune_str
            'all_first': [], # list of rune_str
            'eli_first': [10], # target number of first combo
            'same': [] # list of rune_str
        }
        self.current_board_setting: SettingType = self.default_board_setting
        self.num_col = num_col
        self.num_row = num_row
        self.num_rune = num_rune
        self.board_size = num_col * num_row
        self.mode = mode
        self.empty_rune = Rune(0, False, False)
        self.reset()

    def set_board_setting(self, setting: SettingType):
        new_setting = setting.copy()
        # combine with default setting
        for key in self.default_board_setting:
            if key not in setting:
                new_setting[key] = self.default_board_setting[key]
            else:
                if key == 'eli_first':
                    new_setting[key] = setting[key]
                else:
                    new_setting[key] = self.default_board_setting[key] + setting[key]
        self.current_board_setting = new_setting
        self.set_up_runes()

    def set_up_runes(self):
        for rune_str, num in self.current_board_setting['min_match_color']:
            for i in range(self.num_col * self.num_row):
                if self.board[i].rune == Runes.str2int(rune_str):
                    self.board[i].min_match = num

        for race_str, num in self.current_board_setting['min_match_race']:
            for i in range(self.num_col * self.num_row):
                if self.board[i].race == race_str2int(race_str):
                    self.board[i].min_match = num

        for rune_str in self.current_board_setting['no_first']:
            for i in range(self.num_col * self.num_row):
                if self.board[i].rune == Runes.str2int(rune_str):
                    self.board[i].no_first = True

        for rune_str in self.current_board_setting['all_first']:
            for i in range(self.num_col * self.num_row):
                if self.board[i].rune == Runes.str2int(rune_str):
                    self.board[i].all_first = True

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
            self.board = [Rune(x, 0, False, False) for x in FIXED_BOARD[(self.num_col, self.num_row)]] + [self.empty_rune]
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
    
    def print_race(self):
        race_name_str = ['__', '神', '魔', '人', '獸', '龍', '妖', '機']
        for i in range(self.num_row):
            for j in range(self.num_col):
                idx = i * self.num_col + j
                print(race_name_str[self.board[idx].race], end=' ')
            print()

    def print_min_match(self):
        for i in range(self.num_row):
            for j in range(self.num_col):
                idx = i * self.num_col + j
                print(self.board[idx].min_match, end=' ')
            print()

    def print_untouchable(self):
        for i in range(self.num_row):
            for j in range(self.num_col):
                idx = i * self.num_col + j
                print(self.board[idx].untouchable, end=' ')
            print()

    def rune_str(self) -> str:
        type_str = " WFGLDH?X_U"
        rune_str = ""
        for i in range(self.num_col * self.num_row):
            rune_str += type_str[self.board[i].rune]
        return rune_str
    
    def race_str(self) -> str:
        type_str = " GDHOLEM"
        rune_str = ""
        for i in range(self.num_col * self.num_row):
            rune_str += type_str[self.board[i].race]
        return rune_str
    
    def min_match_str(self) -> str:
        min_match_str = ""
        for i in range(self.num_col * self.num_row):
            min_match_str += str(self.board[i].min_match)
        return min_match_str
    
    # def no_first_str(self) -> str:
    #     no_first_str = ""
    #     for i in range(self.num_col * self.num_row):
    #         no_first_str += str(int(self.board[i].no_first))
    #     return no_first_str
    
    def must_remove_str(self) -> str:
        must_remove_str = ""
        for i in range(self.num_col * self.num_row):
            must_remove_str += str(int(self.board[i].must_remove))
        return must_remove_str
    
    # TODO: obsolete, remove in the future
    def to_c_str(self):
        type_str = " WFGLDH?X_U"
        race_str = " GDEH?"
        rune_str = self.rune_str()
        race_str = self.race_str()
        min_match_str = self.min_match_str()
        must_remove_str = self.must_remove_str()
        
        return rune_str + race_str + min_match_str + must_remove_str
    
    def setting_str(self):
        str1 = 'eli_color: '
        for rune_str in self.current_board_setting['eli_color']:
            str1 += rune_str + ''
        str2 = 'no_first: '
        for rune_str in self.current_board_setting['no_first']:
            str2 += rune_str + ''
        str3 = 'all_first: '
        for rune_str in self.current_board_setting['all_first']:
            str3 += rune_str + ''
        str4 = 'eli_first: ' + str(self.current_board_setting['eli_first'][0])
        str5 = 'same: '
        for rune_str in self.current_board_setting['same']:
            str5 += rune_str + ''
        sep = '/'
        return str1 + sep + str2 + sep + str3 + sep + str4 + sep + str5

                


if __name__ == "__main__":
    board = TosGame()
    board.print_board()

    