import cv2
import numpy as np
import time
from TosGame import TosGame
from Runes import Runes, Rune
from utils import *
from ppadb.device import Device as AdbDevice
from constant import *
from effect.read_effect import read_effects, gen_board_setting
from gen_templates import gen_templates

from gen_templates import FINAL_TEMPLATE_PATH

def read_templates() -> None:
    """
    Read templates for the board recognition.
    """

    if not os.path.exists(FINAL_TEMPLATE_PATH):
        gen_templates()
    assert os.path.exists(FINAL_TEMPLATE_PATH), f'Path {FINAL_TEMPLATE_PATH} does not exist'
    
    global rune_templates, rune_attributes, rune_names, race_template

    load_count = 0
    # for file in os.listdir(TEMPLATE_SAVE_PATH):
    for file in os.listdir(FINAL_TEMPLATE_PATH):
        if file.endswith('.png'):
            file_no_extension = file.split('.')[0]

            # skip for series
            if file_no_extension.endswith('Lin') and not '林黛玉' in TEMPLATE_LOAD_SERIES: continue
            if file_no_extension.endswith('Chen') and not '陳圓圓' in TEMPLATE_LOAD_SERIES: continue
            if file_no_extension.endswith('Chess') and not '棋靈王' in TEMPLATE_LOAD_SERIES: continue
            if file_no_extension.endswith('Jujutsu') and not '咒術' in TEMPLATE_LOAD_SERIES: continue
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

    load_race = 0
    for file in os.listdir(FINAL_RACE_PATH):
        if file.endswith('.png'):
            name = file.split('.')[0]
            race_name = name.split('_')[1]
            race_template[race_name] = cv2.imread(FINAL_RACE_PATH + file, IMREAD_MODE)
            # print(f'Loaded {race_name} template')
            load_race += 1

        
    print(f'Loaded {load_count} runes and {load_race} races templates')
            

def get_grid_loc_processed(x: int, y: int) -> tuple[int, int]:
    return x * RUNE_SIZE // SCALE, y * RUNE_SIZE // SCALE
            

def match_rune(image: MatLike, grid: tuple[int, int], threshold=0.8) -> tuple[Rune, float]:
    """
    Match the rune in the image with the templates.

    Args:
    - image: the image of the board, should be in BGRA format
    - grid: the grid location of the rune
    - threshold: the threshold for the match

    Returns:
    - rune: the string of the rune type
    - attr: the attributes of the rune
    - sim: the similarity of the match
    """
    
    # convert to BGRA if not
    if image.shape[2] != 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    width, height = image.shape[1], image.shape[0]

    margin: int = 2

    x, y = grid

    s_x, s_y = (x * RUNE_SIZE + OFFSET[0]) // SCALE - margin, (y * RUNE_SIZE + OFFSET[1]) // SCALE - margin
    e_x, e_y = (x * RUNE_SIZE + OFFSET2[0]) // SCALE + margin, (y * RUNE_SIZE + OFFSET2[1]) // SCALE + margin

    clamp = lambda x, l, r: max(l, min(r, x))

    s_x, e_x = clamp(s_x, 0, width), clamp(e_x, 0, width)
    s_y, e_y = clamp(s_y, 0, height), clamp(e_y, 0, height)
    
    race_s_x, race_s_y = (x * RUNE_SIZE + RACE_OFFSET[0]) // SCALE - margin, (y * RUNE_SIZE + RACE_OFFSET[1]) // SCALE - margin
    race_e_x, race_e_y = (x * RUNE_SIZE + RACE_OFFSET2[0]) // SCALE + margin, (y * RUNE_SIZE + RACE_OFFSET2[1]) // SCALE + margin 

    race_s_x, race_e_x = clamp(race_s_x, 0, width), clamp(race_e_x, 0, width)
    race_s_y, race_e_y = clamp(race_s_y, 0, width), clamp(race_e_y, 0, width)

    rune_image = image[s_y:e_y, s_x:e_x]
    race_image = image[race_s_y:race_e_y, race_s_x:race_e_x]
    # print(f'boudary of rune_image: ({s_x}, {s_y}), ({e_x}, {e_y})')
    # print(f'boudary of race_image: ({race_s_x}, {race_s_y}), ({race_e_x}, {race_e_y})')

    # print(image.shape)
    # print(race_image.shape)
    # thres1 = 100
    # thres2 = 600
    # edges_img = cv2.Canny(rune_image, thres1, thres2)
    
    max_res = 0.0
    result = 'None'
    attr = (False, False, False)
    name = 'None'
    for rune, templates in rune_templates.items():
        # max_res = 0
        for i, template in enumerate(templates):
            # print(template.shape)
            res = cv2.matchTemplate(rune_image, template, cv2.TM_CCOEFF_NORMED)
            # edge_template = cv2.Canny(template, thres1, thres2)
            # res = cv2.matchTemplate(edges_img, edge_template, cv2.TM_CCOEFF_NORMED)
            m_res = float(np.max(res))
            if m_res > max_res:
                max_res = m_res
                result = rune
                attr = rune_attributes[rune][i]
                name = rune_names[rune][i]


    if max_res < threshold:
        result = 'unknown'
    max_race_res = 0.0
    race_str = ""
    for race, template in race_template.items():
        # print('template shape:', template.shape)
        small_template = cv2.resize(template, (template.shape[1] // SCALE, template.shape[0] // SCALE))
        if small_template.shape[1] > race_image.shape[1]:
            small_template = small_template[:, 0:race_image.shape[1]]
        # print(small_template.shape, race_image.shape)
        mask = small_template[:, :, 3]
        res = cv2.matchTemplate(race_image, small_template, cv2.TM_CCORR_NORMED, mask=mask)
        m_res = float(np.max(res))
        # print(m_res)
        # cv2.imshow("small_template", small_template)
        # cv2.imshow("race img", race_image)
        # cv2.imshow('mask', mask)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        if m_res > max_race_res and m_res > 0.85:
            race_str = race
            max_race_res = m_res
            # print(race_int)
    # print(f'{race_str}: {max_race_res:.2f}')

    result_rune = Rune(rune=Runes.str2int(result), race=race_str2int(race_str), untouchable=attr[0], must_remove=attr[2])

    return result_rune, max_res

# @timeit
def read_board(device: AdbDevice = None, filepath: str|None = None, screenshot: MatLike|None = None) -> TosGame:

    if rune_templates['water'] == []:
        read_templates()

    if device is None and filepath is None and screenshot is None:
        device = get_adb_device()

    if screenshot is None:
        if filepath is None:
            pic = device.screencap()
            screenshot = cv2.imdecode(np.frombuffer(pic, np.uint8), IMREAD_MODE)
            print('screenshot shape:', screenshot.shape)
        else:
            assert os.path.exists(filepath), f'File {filepath} does not exist'
            screenshot = cv2.imread(filepath, IMREAD_MODE)

    screenshot_3channel = screenshot.copy()
    if screenshot_3channel.shape[2] != 3:
        screenshot_3channel = cv2.cvtColor(screenshot_3channel, cv2.COLOR_BGRA2BGR)

    if screenshot.shape[2] != 4:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGRA)
        

    s_x, s_y = get_grid_loc(0, 0)
    e_x, e_y = get_grid_loc(COL_NUM, ROW_NUM)
    screenshot = screenshot[s_y:e_y, s_x:e_x]
    screenshot = cv2.resize(screenshot, (screenshot.shape[1] // SCALE, screenshot.shape[0] // SCALE))

    runes = []
    for y in range(ROW_NUM):
        for x in range(COL_NUM):
            rune, sim = match_rune(screenshot, (x, y), threshold=0.7)
            runes.append(rune)
            # print(rune.__repr__)
        #     print(f'{sim:.2f}', end=' ')
        # print()

    game = TosGame()
    runes.append(game.empty_rune)
    game.set_board(runes)
    # screenshot = cv2.cvtColor(screenshot_copy, cv2.COLOR_BGRA2BGR)
    effects = read_effects(screenshot_3channel)
    setting = gen_board_setting(effects)
    print(setting)
    game.set_board_setting(setting)
    # game.set_up_runes()

    return game

def test_screenshot(filename='E:/screenshot.png'):
    assert os.path.exists(filename), f'File {filename} does not exist'
    board = read_board(None, filename)
    board.print_board()

def test_rune_at(x, y):
    screenshot = cv2.imread('E:/screenshot.png', IMREAD_MODE)
    rune = match_rune(screenshot, (x, y))
    print(rune)




if __name__ == "__main__":

    # device = get_adb_device()
    # game = read_board(device, 'screenshots/Screenshot_20240323-012216.png')
    game = read_board(None, 'screenshots/Screenshot_20240323-012316.png')
    game.set_up_runes()
    game.print_board()
    # print("Races:")
    # game.print_race()
    # print("Min match:")
    # game.print_min_match()
    # print("Untouchable:")
    # game.print_untouchable()
    



    