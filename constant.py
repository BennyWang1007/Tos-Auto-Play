import numpy as np
import cv2
from typing import Literal
from cv2.typing import MatLike

SeriesName = Literal['棋靈王', '林黛玉', '陳圓圓']

# to change
# SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 2280
# LEFT_TOP = (0, 1210)

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 1600 # the resolution of the device
LEFT_TOP = (0, 770) # the top left corner of the board

NUM_COL = 6
NUM_ROW = 5
MODE = 'random'
MAX_DEPTH = 12

TEMPLATE_LOAD_SERIES: list[SeriesName] = ["棋靈王", "林黛玉", "陳圓圓"]

"""--------------------------------------------------------------------------------------
Do not modify these variable below this line unless you know what you are doing
"""

RUNE_SIZE = SCREEN_WIDTH // 6
RUNE_SIZE_SAMPLE = 150

TEMPLATE_128_PATH = 'template_128/'
TEMPLATE_150_PATH = f'template_150/'
TEMPLATE_SAVE_PATH = f'template_{RUNE_SIZE}/'
FINAL_TEMPLATE_PATH = f'template_{RUNE_SIZE}_final/'

# SAMPLE_SIZE = 60
# SAMPLE_OFFSET = (RUNE_SIZE_SAMPLE - SAMPLE_SIZE) // 2

# select the bottom half of the rune
SAMPLE_OFFSET = 45, RUNE_SIZE_SAMPLE // 2
SAMPLE_OFFSET2 = RUNE_SIZE_SAMPLE - 45, RUNE_SIZE_SAMPLE - 30

# SAMPLE_SIZE = RUNE_SIZE_SAMPLE - 45, RUNE_SIZE_SAMPLE // 2
SCALE2 = 3

# OFFSET = (RUNE_SIZE - SAMPLE_SIZE * RUNE_SIZE // RUNE_SIZE_SAMPLE) // 2
OFFSET = SAMPLE_OFFSET[0] * RUNE_SIZE // RUNE_SIZE_SAMPLE, SAMPLE_OFFSET[1] * RUNE_SIZE // RUNE_SIZE_SAMPLE
OFFSET2 = SAMPLE_OFFSET2[0] * RUNE_SIZE // RUNE_SIZE_SAMPLE, SAMPLE_OFFSET2[1] * RUNE_SIZE // RUNE_SIZE_SAMPLE

IMREAD_MODE = cv2.IMREAD_UNCHANGED

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

# obsolete variable
FIXED_BOARD: dict[tuple[int, int], np.ndarray] = {
    # (3, 3): np.array(
    #     [
    #         [3, 3, 1],
    #         [2, 1, 2],
    #         [3, 2, 1]
    #     ]
    # ),
    # (4, 4): np.array(
    #     [
    #         [3, 3, 1, 1],
    #         [2, 1, 2, 2],
    #         [3, 1, 2, 1],
    #         [3, 2, 1, 1]
    #     ]
    # ),
    # (5, 4): np.array(
    #     [
    #         [4, 3, 1, 1, 4],
    #         [2, 1, 2, 2, 3],
    #         [3, 1, 2, 1, 4],
    #         [3, 2, 1, 1, 4]
    #     ]
    # ),
    # (5, 5): np.array(
    #     [
    #         [2, 6, 3, 1, 1],
    #         [6, 3, 3, 4, 6],
    #         [1, 5, 5, 1, 4],
    #         [5, 2, 6, 6, 4],
    #         [2, 4, 1, 1, 2]
    #     ]
    # ),
    # (6, 5): np.array(
    #     [
    #         [4, 2, 5, 1, 4, 3], 
    #         [3, 6, 3, 2, 3, 3], 
    #         [3, 4, 2, 5, 2, 1], 
    #         [2, 3, 5, 1, 2, 2], 
    #         [5, 2, 5, 4, 3, 3]
    #     ]
    # )
}