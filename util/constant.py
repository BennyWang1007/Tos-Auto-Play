from typing import Literal
import configparser

import os
import numpy as np

MatLike = np.ndarray
Complexity = Literal["Low", "Mid", "High", "Extreme"]
SeriesName = Literal["棋靈王", "林黛玉", "陳圓圓", "咒術"]

# the directory of the project
DIR = os.path.join(os.path.dirname(__file__), '..')

config = configparser.ConfigParser()
config_path = os.path.join(DIR, 'config.ini')
config.read(config_path)

SCREEN_WIDTH = int(config['device']['screen_width'])
SCREEN_HEIGHT = int(config['device']['screen_height'])
LEFT_TOP = (int(config['device']['lefttop_x']), int(config['device']['lefttop_y']))
# print(SCREEN_WIDTH, SCREEN_HEIGHT, LEFT_TOP)
# SCREEN_WIDTH, SCREEN_HEIGHT = 900, 1600 # the resolution of the device
# LEFT_TOP = (0, 770) # the top left corner of the board

COL_NUM = 6
ROW_NUM = 5
MODE = 'random'
MAX_DEPTH = 12

def convert_series_name(series: str) -> SeriesName:
    if series == "chess":
        return "棋靈王"
    elif series == "lin":
        return "林黛玉"
    elif series == "chen":
        return "陳圓圓"
    elif series == "jujutsu":
        return "咒術"
    else:
        raise ValueError(f"Invalid series name: {series}")
if config['template']['series'] == "none":
    TEMPLATE_LOAD_SERIES = []
elif config['template']['series'] == "all":
    TEMPLATE_LOAD_SERIES = ["棋靈王", "林黛玉", "陳圓圓", "咒術"]
else:
    TEMPLATE_LOAD_SERIES = config['template']['series'].split(', ')
    TEMPLATE_LOAD_SERIES = [convert_series_name(series) for series in TEMPLATE_LOAD_SERIES]
# print(TEMPLATE_LOAD_SERIES)
# TEMPLATE_LOAD_SERIES: list[SeriesName] = ["林黛玉", "陳圓圓"]

"""--------------------------------------------------------------------------------------
Do not modify these variable below this line unless you know what you are doing
"""

RUNE_SIZE = SCREEN_WIDTH // 6
RUNE_SIZE_SAMPLE = 150

TEMPLATE_128_PATH = os.path.join(DIR, 'templates', 'template_128/')
TEMPLATE_SAVE_PATH = os.path.join(DIR, f'templates/template_{RUNE_SIZE}/')
FINAL_TEMPLATE_PATH = os.path.join(DIR, f'templates/template_{RUNE_SIZE}_final/')

CD_TEMPLATE_PATH = os.path.join(DIR, 'templates', 'cd.png')

# TEMPLATE_SAVE_PATH = f'E:/template_{RUNE_SIZE}/'
# FINAL_TEMPLATE_PATH = f'E:/template_{RUNE_SIZE}_final/'

RACE_TEMPLATE_PATH = TEMPLATE_128_PATH + 'race/'
FINAL_RACE_PATH = FINAL_TEMPLATE_PATH + 'race/'

# select the bottom half of the rune as templates
SAMPLE_OFFSET = 45, RUNE_SIZE_SAMPLE // 2
SAMPLE_OFFSET2 = RUNE_SIZE_SAMPLE - 45, RUNE_SIZE_SAMPLE - 30

# scale down constant
SCALE = 3

# transformed offset to the screen size
OFFSET = SAMPLE_OFFSET[0] * RUNE_SIZE // RUNE_SIZE_SAMPLE, SAMPLE_OFFSET[1] * RUNE_SIZE // RUNE_SIZE_SAMPLE
OFFSET2 = SAMPLE_OFFSET2[0] * RUNE_SIZE // RUNE_SIZE_SAMPLE, SAMPLE_OFFSET2[1] * RUNE_SIZE // RUNE_SIZE_SAMPLE

RACE_SIZE = 68 * RUNE_SIZE // RUNE_SIZE_SAMPLE
RACE_OFFSET = int(RUNE_SIZE * 0.6), 0
RACE_OFFSET2 = RACE_OFFSET[0] + RACE_SIZE, RACE_OFFSET[1] + RACE_SIZE

IMREAD_MODE = -1 # cv2.IMREAD_UNCHANGED
GET_ROUTE_EXE_PATH = os.path.join(DIR, 'c++', 'get_route.exe')

SettingType = dict[str, list[str | tuple[str, int] | int]]

race_template: dict[str, MatLike] = {}

rune_templates: dict[str, list[MatLike]] = {
    'water': [],
    'fire': [],
    'grass': [],
    'light': [],
    'dark': [],
    'heart': [], 
    'hidden': []
}

# dict of (untouchable, eliminable, must_remove)
rune_attributes: dict[str, dict[int, tuple[bool, bool, bool]]] = {
    'water': {},
    'fire': {},
    'grass': {},
    'light': {},
    'dark': {},
    'heart': {}, 
    'hidden': {}
}

rune_names: dict[str, list[str]] = {
    'water': [],
    'fire': [],
    'grass': [],
    'light': [],
    'dark': [],
    'heart': [], 
    'hidden': []
}




FIXED_BOARD: dict[tuple[int, int], list[int]] = {
    (3, 3): [3, 3, 1] +
            [2, 1, 2] +
            [3, 2, 1]
    ,
    (4, 4): [3, 3, 1, 1] +
            [2, 1, 2, 2] +
            [3, 1, 2, 1] +
            [3, 2, 1, 1]
    ,
    (5, 4): [4, 3, 1, 1, 4] +
            [2, 1, 2, 2, 3] +
            [3, 1, 2, 1, 4] +
            [3, 2, 1, 1, 4]
    ,
    (5, 5): [2, 6, 3, 1, 1] +
            [6, 3, 3, 4, 6] +
            [1, 5, 5, 1, 4] +
            [5, 2, 6, 6, 4] +
            [2, 4, 1, 1, 2]
    ,
    (6, 5): [4, 2, 5, 1, 4, 3] +
            [3, 6, 3, 2, 3, 3] +
            [3, 4, 2, 5, 2, 1] +
            [2, 3, 5, 1, 2, 2] +
            [5, 2, 5, 4, 3, 3]
}