import numpy as np
import cv2
from ppadb.device import Device as AdbDevice

# to change
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 2280
LEFT_TOP = (0, 1210)
# SCREEN_WIDTH, SCREEN_HEIGHT = 900, 1600
# LEFT_TOP = (0, 770)

NUM_COL = 6
NUM_ROW = 5
MODE = 'fixed'
MAX_DEPTH = 12

# Do not modify these variable below this line unless you know what you are doing
RUNE_SIZE = SCREEN_WIDTH // 6
RUNE_SIZE_SAMPLE = 150

SAMPLE_SIZE = 60
SAMPLE_OFFSET = (RUNE_SIZE_SAMPLE - SAMPLE_SIZE) // 2

SCALE2 = 2

OFFSET = (RUNE_SIZE - SAMPLE_SIZE * RUNE_SIZE // RUNE_SIZE_SAMPLE) // 2

IMREAD_MODE = cv2.IMREAD_UNCHANGED

TEMPLATE_128_PATH = 'template_128/'
TEMPLATE_150_PATH = f'template_150/'
TEMPLATE_SAVE_PATH = f'template_{RUNE_SIZE}/'

rune_templates: dict[str, list[np.ndarray]] = {
    'water': [],
    'fire': [],
    'grass': [],
    'light': [],
    'dark': [],
    'heart': [], 
    'hidden': []
}

# dict of (untouchable, eliminable, must_remove)
rune_attributes = {
    'water': {},
    'fire': {},
    'grass': {},
    'light': {},
    'dark': {},
    'heart': {}, 
    'hidden': {}
}

rune_names = {
    'water': [],
    'fire': [],
    'grass': [],
    'light': [],
    'dark': [],
    'heart': [], 
    'hidden': []
}

FIXED_BOARD: dict[tuple[int, int], np.ndarray] = {
    (3, 3): np.array(
        [
            [3, 3, 1],
            [2, 1, 2],
            [3, 2, 1]
        ]
    ),
    (4, 4): np.array(
        [
            [3, 3, 1, 1],
            [2, 1, 2, 2],
            [3, 1, 2, 1],
            [3, 2, 1, 1]
        ]
    ),
    (5, 4): np.array(
        [
            [4, 3, 1, 1, 4],
            [2, 1, 2, 2, 3],
            [3, 1, 2, 1, 4],
            [3, 2, 1, 1, 4]
        ]
    ),
    (5, 5): np.array(
        [
            [2, 6, 3, 1, 1],
            [6, 3, 3, 4, 6],
            [1, 5, 5, 1, 4],
            [5, 2, 6, 6, 4],
            [2, 4, 1, 1, 2]
        ]
    ),
    (6, 5): np.array(
        [
            [4, 2, 5, 1, 4, 3], 
            [3, 6, 3, 2, 3, 3], 
            [3, 4, 2, 5, 2, 1], 
            [2, 3, 5, 1, 2, 2], 
            [5, 2, 5, 4, 3, 3]
        ]
    )
}