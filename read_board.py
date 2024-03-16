import cv2
import numpy as np
import time
from TosGame import TosGame
from Runes import Runes, Rune
from utils import *
from ppadb.device import Device as AdbDevice
from constant import *

from gen_templates import FINAL_TEMPLATE_PATH

def read_templates() -> None:
    """
    Read templates for the board recognition.
    """

    # assert os.path.exists(TEMPLATE_SAVE_PATH), f'Path {TEMPLATE_SAVE_PATH} does not exist'
    assert os.path.exists(FINAL_TEMPLATE_PATH), f'Path {FINAL_TEMPLATE_PATH} does not exist'
    global rune_templates, rune_attributes, rune_names

    load_count = 0
    # for file in os.listdir(TEMPLATE_SAVE_PATH):
    for file in os.listdir(FINAL_TEMPLATE_PATH):
        if file.endswith('.png'):
            file_no_extension = file.split('.')[0]

            # skip for series
            if file_no_extension.endswith('Lin') and not '林黛玉' in TEMPLATE_LOAD_SERIES:
                continue
            if file_no_extension.endswith('Chen') and not '陳圓圓' in TEMPLATE_LOAD_SERIES:
                continue
            if file_no_extension.endswith('Chess') and not '棋靈王' in TEMPLATE_LOAD_SERIES:
                continue
            rune_type = ''
            untouchable = False
            eliminable = True
            must_remove = False
            if file[0] == 'w': rune_type = 'water'
            elif file[0] == 'f': rune_type = 'fire'
            elif file[0] == 'p': rune_type = 'grass'
            elif file[0] == 'l': rune_type = 'light'
            elif file[0] == 'd': rune_type = 'dark'
            elif file[0] == 'h': rune_type = 'heart'
            elif file[0] == 'q': rune_type = 'hidden'
            else: continue

            load_count += 1

            if '0' in file: must_remove = False # rune ready to be frozen
            elif '1' in file: eliminable = False # frozen rune by 3 turns
            elif '2' in file: eliminable = False # frozen rune by 2 turns
            elif '3' in file: eliminable = False # frozen rune by 1 turn

            if 'x' in file: untouchable = True # 風化符石
            if 'k' in file: must_remove = True # 腐化符石

            template = cv2.imread(FINAL_TEMPLATE_PATH + file, IMREAD_MODE)
            
            # # template = template[SAMPLE_OFFSET:SAMPLE_OFFSET + SAMPLE_SIZE, SAMPLE_OFFSET:SAMPLE_OFFSET + SAMPLE_SIZE]
            # s = SAMPLE_OFFSET * RUNE_SIZE // RUNE_SIZE_SAMPLE
            # e = (SAMPLE_OFFSET + SAMPLE_SIZE) * RUNE_SIZE // RUNE_SIZE_SAMPLE
            # template = template[s:e, s:e]
            
            template = cv2.resize(template, (template.shape[1] // SCALE, template.shape[0] // SCALE))

            if rune_templates.get(rune_type) is None:
                idx = 0
                rune_templates[rune_type] = [template]
            else:
                idx = len(rune_templates[rune_type])
                rune_templates[rune_type].append(template)

            rune_attributes[rune_type][idx] = (untouchable, eliminable, must_remove)
            
            rune_names[rune_type].append(file_no_extension)
        
    print(f'Loaded {load_count} templates')
            

def get_grid_loc_processed(x: int, y: int) -> tuple[int, int]:
    return x * RUNE_SIZE // SCALE, y * RUNE_SIZE // SCALE
            

def match_rune(image, grid: tuple[int, int], threshold=0.8) -> tuple[str, tuple[bool, bool, bool], float]:
    """
    Match the rune in the image with the templates.

    Args:
    - image: the image of the board
    - grid: the grid location of the rune
    - threshold: the threshold for the match

    Returns:
    - rune: the string of the rune type
    - attr: the attributes of the rune
    - sim: the similarity of the match
    """
    # image = cv2.resize(image, (image.shape[1] // SCALE, image.shape[0] // SCALE))

    width, height = image.shape[1], image.shape[0]

    margin = 2

    # s_x, s_y = get_grid_loc(*grid)
    # e_x, e_y = s_x, s_y

    # s_x = int((s_x + OFFSET[0]) // SCALE - margin)
    # s_y = int((s_y + OFFSET[1]) // SCALE - margin)
    # e_x = int((e_x + OFFSET2[0]) // SCALE + margin)
    # e_y = int((e_y + OFFSET2[1]) // SCALE + margin)
    x, y = grid

    s_x, s_y = (x * RUNE_SIZE + OFFSET[0]) // SCALE - margin, (y * RUNE_SIZE + OFFSET[1]) // SCALE - margin
    e_x, e_y = (x * RUNE_SIZE + OFFSET2[0]) // SCALE + margin, (y * RUNE_SIZE + OFFSET2[1]) // SCALE + margin

    clamp = lambda x, l, r: max(l, min(r, x))

    s_x, e_x = clamp(s_x, 0, width), clamp(e_x, 0, width)
    s_y, e_y = clamp(s_y, 0, height), clamp(e_y, 0, height)
    
    image = image[s_y:e_y, s_x:e_x]
    # print(image.shape)
    
    max_res = 0.0
    result = 'None'
    attr = (False, False, False)
    name = 'None'
    for rune, templates in rune_templates.items():
        # max_res = 0
        for i, template in enumerate(templates):
            # print(template.shape)
            res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            m_res = float(np.max(res))
            if m_res > max_res:
                max_res = m_res
                result = rune
                attr = rune_attributes[rune][i]
                name = rune_names[rune][i]
            # if rune_names[rune][i] == 'd':
            #     print(f'{name}: {m_res:.2f}')
            #     cv2.imshow('template', template)
            #     cv2.imshow('image', image)
            #     cv2.waitKey(0)
            #     cv2.destroyAllWindows()
            #     quit()
                
    if max_res > threshold:
        return result, attr, max_res
    else:
        return 'unknown', (False, False, False), max_res

@timeit
def read_board(device: AdbDevice = None, filepath: str|None = None) -> TosGame:

    if device is None and filepath is None:
        device = get_adb_device()

    if filepath is None:
        pic = device.screencap()
        screenshot = cv2.imdecode(np.frombuffer(pic, np.uint8), IMREAD_MODE)
    else:
        assert os.path.exists(filepath), f'File {filepath} does not exist'
        screenshot = cv2.imread(filepath, IMREAD_MODE)

    if screenshot.shape[2] != 4:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGRA)

    board_arr = []
    untouch_arr = []
    must_remove_arr = []

    s_x, s_y = get_grid_loc(0, 0)
    e_x, e_y = get_grid_loc(NUM_COL, NUM_ROW)
    screenshot = screenshot[s_y:e_y, s_x:e_x]
    screenshot = cv2.resize(screenshot, (screenshot.shape[1] // SCALE, screenshot.shape[0] // SCALE))

    for y in range(NUM_ROW):
        for x in range(NUM_COL):
            rune, attr, sim = match_rune(screenshot, (x, y))
            untouch_arr.append(attr[0])
            must_remove_arr.append(attr[2])
            board_arr.append(Runes.str2int(rune))
        #     print(f'{sim:.2f}', end=' ')
        # print()

    board = TosGame()
    runes = [Rune(board_arr[x], untouch_arr[x], must_remove_arr[x]) for x in range(NUM_COL * NUM_ROW)] + [Rune(0, False, False)]
    board.set_board(runes)

    return board

def test_screenshot(filename='E:/screenshot.png'):
    assert os.path.exists(filename), f'File {filename} does not exist'
    board = read_board(None, filename)
    board.print_board()

def test_rune_at(x, y):
    screenshot = cv2.imread('E:/screenshot.png', IMREAD_MODE)
    rune = match_rune(screenshot, (x, y))
    print(rune)




if __name__ == "__main__":

    device = get_adb_device()
    read_templates()

    # board = read_board()
    # board.print_board()
    # test_screenshot('E:/screenshot2.png')
    # test_screenshot('screenshots/screenshot2.png')
    # test_screenshot('screenshots/screenshot3.png')
    # test_screenshot('screenshots/screenshot4.png')
    board = read_board(device, 'E:/screenshot2.png')
    # board = read_board(device)
    board.print_board()
    with open('input.txt', 'w') as f:
        f.write(str(board))
    



    