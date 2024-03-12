

from utils import *
import cv2
from Board import Board
from Runes import Runes
import numpy as np
import time
from ppadb.client import Client
from ppadb.device import Device as AdbDevice
from constant import *

def read_templates() -> None:
    """
    Read templates for the board recognition.
    """

    assert os.path.exists(TEMPLATE_SAVE_PATH), f'Path {TEMPLATE_SAVE_PATH} does not exist'
    global rune_templates, rune_attributes, rune_names

    for file in os.listdir(TEMPLATE_SAVE_PATH):
        if file.endswith('.png'):
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

            if '0' in file: must_remove = False # rune ready to be frozen
            elif '1' in file: eliminable = False # frozen rune by 3 turns
            elif '2' in file: eliminable = False # frozen rune by 2 turns
            elif '3' in file: eliminable = False # frozen rune by 1 turn

            if 'x' in file: untouchable = True # 風化符石
            if 'k' in file: must_remove = True # 腐化符石

            template = cv2.imread(TEMPLATE_SAVE_PATH + file, IMREAD_MODE)
            
            # template = template[SAMPLE_OFFSET:SAMPLE_OFFSET + SAMPLE_SIZE, SAMPLE_OFFSET:SAMPLE_OFFSET + SAMPLE_SIZE]
            s = SAMPLE_OFFSET * RUNE_SIZE // RUNE_SIZE_SAMPLE
            e = (SAMPLE_OFFSET + SAMPLE_SIZE) * RUNE_SIZE // RUNE_SIZE_SAMPLE
            template = template[s:e, s:e]
            
            template = cv2.resize(template, (template.shape[1] // SCALE2, template.shape[0] // SCALE2))

            if rune_templates.get(rune_type) is None:
                idx = 0
                rune_templates[rune_type] = [template]
            else:
                idx = len(rune_templates[rune_type])
                rune_templates[rune_type].append(template)

            rune_attributes[rune_type][idx] = (untouchable, eliminable, must_remove)
            no_extension = file.split('.')[0]
            rune_names[rune_type].append(no_extension)
            # print(no_extension)
            

def match_rune(image, grid, threshold=0.8):

    image = cv2.resize(image, (image.shape[1] // SCALE2, image.shape[0] // SCALE2))

    width, height = image.shape[1], image.shape[0]

    margin = 2

    s_x, s_y = get_grid_loc(*grid)
    e_x, e_y = get_grid_loc(grid[0] + 1, grid[1] + 1)

    s_x = int((s_x + SAMPLE_OFFSET * RUNE_SIZE / RUNE_SIZE_SAMPLE) // SCALE2 - margin)
    s_y = int((s_y + SAMPLE_OFFSET * RUNE_SIZE / RUNE_SIZE_SAMPLE) // SCALE2 - margin)
    e_x = int((e_x - SAMPLE_OFFSET * RUNE_SIZE / RUNE_SIZE_SAMPLE) // SCALE2 + margin)
    e_y = int((e_y - SAMPLE_OFFSET * RUNE_SIZE / RUNE_SIZE_SAMPLE) // SCALE2 + margin)

    clamp = lambda x, l, r: max(l, min(r, x))

    s_x, e_x = clamp(s_x, 0, width), clamp(e_x, 0, width)
    s_y, e_y = clamp(s_y, 0, height), clamp(e_y, 0, height)
    
    image = image[s_y:e_y, s_x:e_x]
    # print(image.shape)
    
    max_res = 0
    result = 'None'
    attr = (False, False, False)
    name = 'None'
    for rune, templates in rune_templates.items():
        # max_res = 0
        for i, template in enumerate(templates):
            # print(template.shape)
            res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            m_res = np.max(res)
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

# @timeit
def read_board(device: AdbDevice = None, filepath: str = None) -> Board:

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

    start_t = time.time()

    board_arr = []
    untouch_arr = []
    eliminable_arr = []
    must_remove_arr = []
    for y in range(5):
        arr = []
        un_arr = []
        el_arr = []
        must_r_arr = []
        for x in range(6):
            rune, attr, sim = match_rune(screenshot, (x, y))
            # rune, sim = match_rune2(screenshot, (x, y))
            un_arr.append(attr[0])
            el_arr.append(attr[1])
            must_r_arr.append(attr[2])
            arr.append(Runes.str2int(rune))
            print(f'{sim:.2f}', end=' ')

        untouch_arr.append(un_arr)
        eliminable_arr.append(el_arr)
        must_remove_arr.append(must_r_arr)
        board_arr.append(arr)
        print()

    board = Board()
    board.set_board(np.array(board_arr))
    board.set_untouchable(np.array(untouch_arr))
    board.set_eliminable(np.array(eliminable_arr))
    board.set_must_remove(np.array(must_remove_arr))

    print(f'time elapsed: {time.time() - start_t:.2f} seconds')

    return board

def test_screenshot(filename='E:/screenshot.png'):
    assert os.path.exists(filename), f'File {filename} does not exist'
    screenshot = cv2.imread(filename, IMREAD_MODE)
    if screenshot.shape[2] != 4:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGRA)
    runes = []
    for y in range(5):
        row = []
        for x in range(6):
            rune, attr, sim = match_rune(screenshot, (x, y))
            # rune, sim = match_rune2(screenshot, (x, y))
            print(f'{sim:.2f}', end=' ')
            row.append(Runes.str2int(rune))
        runes.append(row)
        print()
    print_board(np.array(runes))

def test_rune_at(x, y):
    screenshot = cv2.imread('E:/screenshot.png', IMREAD_MODE)
    rune = match_rune(screenshot, (x, y))
    print(rune)




if __name__ == "__main__":

    device = get_adb_device()
    read_templates()

    # board = read_board()
    # board.print_board()
    # test_screenshot('screenshots/screenshot.png')
    # test_screenshot('screenshots/screenshot2.png')
    # test_screenshot('screenshots/screenshot3.png')
    # test_screenshot('screenshots/screenshot4.png')
    board = read_board(device)
    board.print_board()

    print('untouchable:')
    print(board.untouchable)
    print('eliminable:')
    print(board.eliminable)
    print('must_remove:')
    print(board.must_remove)


    