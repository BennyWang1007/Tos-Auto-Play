import cv2
import numpy as np
import os
from typing import Tuple, List

from constant import TEMPLATE_128_PATH, TEMPLATE_SAVE_PATH, RUNE_SIZE


def gen_templates() -> None:
    """
    Generate templates for the board recognition.
    """

    assert os.path.exists(TEMPLATE_128_PATH), f'Path {TEMPLATE_128_PATH} does not exist'

    if not os.path.exists(TEMPLATE_SAVE_PATH):
        os.makedirs(TEMPLATE_SAVE_PATH)
    
    extra_image = cv2.imread(TEMPLATE_128_PATH + 'extra.png', cv2.IMREAD_UNCHANGED)
    size = (int(extra_image.shape[1] * 150 / RUNE_SIZE), int(extra_image.shape[0] * 150 / RUNE_SIZE))
    extra_image = cv2.resize(extra_image, size)
    for file in os.listdir(TEMPLATE_128_PATH):
        if file.endswith('.png'):

            if os.path.exists(TEMPLATE_SAVE_PATH + file):
                print(f'{file} already exists')
                continue

            if file[0] not in ['w', 'f', 'p', 'l', 'd', 'h', 'q']:
                continue

            template = cv2.imread(TEMPLATE_128_PATH + file, cv2.IMREAD_UNCHANGED)
            template = cv2.resize(template, (RUNE_SIZE, RUNE_SIZE))
            cv2.imwrite(TEMPLATE_SAVE_PATH + file, template)

            x1, x2 = int(RUNE_SIZE * 0.6), int(RUNE_SIZE * 0.6) + extra_image.shape[1]
            x2 = min(x2, RUNE_SIZE)
            y1, y2 = 0, extra_image.shape[0]

            alpha_s = extra_image[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                for x in range(x1, x2):
                    for y in range(y1, y2):
                        template[y, x, c] = (alpha_s[y - y1, x - x1] * extra_image[y - y1, x - x1, c] +
                                            alpha_l[y - y1, x - x1] * template[y, x, c])
                        
            no_extension = file.split('.')[0]
            cv2.imwrite(TEMPLATE_SAVE_PATH + no_extension + '_e.png', template)

if __name__ == '__main__':
    gen_templates()