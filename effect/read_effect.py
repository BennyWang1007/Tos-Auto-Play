
import os
from typing import Tuple

import cv2
import numpy as np
from cv2.typing import MatLike

from util.constant import SettingType, CD_TEMPLATE_PATH
from util.utils import timeit
from .constant import *

EFFECT_IMREAD_FLAG = cv2.IMREAD_UNCHANGED

to_setting: dict[str, dict] = {}

def gen_templates_effect():
    count = 0
    for effect_name, effect_ids in EFFECT_NAMES.items():
        for effect_id in effect_ids:
            # fill the effect id to 3 digits with 0
            effect_id = str(effect_id).zfill(3)
            if not os.path.exists(FINAL_EFFECT_PATH):
                os.makedirs(FINAL_EFFECT_PATH)
            template = cv2.imread(f'{EFFECT_PATH}/ICON{effect_id}.png', cv2.IMREAD_UNCHANGED)
            template = cv2.resize(template, (EFFECT_TEMPLATE_SIZE, EFFECT_TEMPLATE_SIZE))
            cv2.imwrite(f'{FINAL_EFFECT_PATH}ICON{effect_id}.png', template)
            count += 1

    print(f'{count} effect templates generated.')


def set_toSetting() -> None:
    global EFFECT_NAMES, to_setting
    for effect_name, _ in EFFECT_NAMES.items():
        if effect_name.startswith('SAME'):
            colors = effect_name[5:]
            color_list = [color for color in colors]
            to_setting[effect_name] = {'same': color_list}

        elif effect_name.startswith('No'):
            color = effect_name[2]
            to_setting[effect_name] = {'no_first': [color]}

        elif effect_name[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if effect_name[1] == 'F':
                to_setting[effect_name] = {'eli_first': int(effect_name[0])}
            elif (effect_name[1] == '0' and effect_name[2] == 'F'):
                to_setting[effect_name] = {'eli_first': 10}

        elif effect_name.startswith('ELI'):
            colors = effect_name[4:]
            color_list = [color for color in colors if color != '+']
            to_setting[effect_name] = {'eli_color': [color for color in color_list]}

        else:
            to_setting[effect_name] = {}


# @timeit
def read_effect_templates() -> None:
    """
    Read templates for the board recognition.
    """

    global EFFECT_TEMPLATES, EFFECT_MASKS

    if not os.path.exists(FINAL_EFFECT_PATH):
        gen_templates_effect()

    for effect_name, effect_ids in EFFECT_NAMES.items():
        for effect_id in effect_ids:
            effect_id_str = str(effect_id).zfill(3)
            template = cv2.imread(f'{FINAL_EFFECT_PATH}/ICON{effect_id_str}.png', cv2.IMREAD_UNCHANGED)
            assert template.shape == (EFFECT_TEMPLATE_SIZE, EFFECT_TEMPLATE_SIZE, 4), f'Incorrect shape {template.shape} for {effect_name}'
            if template is None:
                raise ValueError(f'Cannot read {FINAL_EFFECT_PATH}/ICON{effect_id_str}.png')
            if effect_name in EFFECT_TEMPLATES:
                # EFFECT_TEMPLATES[effect_name].append(template)
                EFFECT_MASKS[effect_name].append(template[:, :, 3])
                if EFFECT_IMREAD_FLAG == cv2.IMREAD_UNCHANGED:
                    EFFECT_TEMPLATES[effect_name].append(cv2.cvtColor(template, cv2.COLOR_BGRA2BGR))
                elif EFFECT_IMREAD_FLAG == cv2.IMREAD_GRAYSCALE:
                    EFFECT_TEMPLATES[effect_name].append(cv2.cvtColor(template, cv2.COLOR_BGR2GRAY))
            else:
                EFFECT_MASKS[effect_name] = [template[:, :, 3]]
                # EFFECT_TEMPLATES[effect_name] = [cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)]
                if EFFECT_IMREAD_FLAG == cv2.IMREAD_UNCHANGED:
                    EFFECT_TEMPLATES[effect_name] = [cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)]
                elif EFFECT_IMREAD_FLAG == cv2.IMREAD_GRAYSCALE:
                    EFFECT_TEMPLATES[effect_name] = [cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)]

    # print(EFFECT_TEMPLATES)

# @timeit
def read_effect(image: np.ndarray, threshold=0.75) -> list:
    effects: list = []
    results: list[tuple] = []
    found_loc: list[tuple[int, int]] = []
    _image = cv2.resize(image, (0, 0), fx=EFFECT_SCALE, fy=EFFECT_SCALE)
    for effect_name, templates in EFFECT_TEMPLATES.items():
        for i in range(len(templates)):
            template = templates[i]
            mask = EFFECT_MASKS[effect_name][i]
            # print(_image.shape, template.shape, mask.shape)
            res = cv2.matchTemplate(_image, template, cv2.TM_CCOEFF_NORMED, mask=mask)
            res[np.isinf(res)] = 0

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            loc = np.where(res >= threshold)
            if len(loc[0]) > 0:
                found_loc.append((loc[1][0], loc[0][0]))
            
    found_loc = list(set(found_loc))
    if len(found_loc) == 0:
        return []
    # print(found_loc)

    effects = []
    results = []
    for x, y in found_loc:
        test_image = _image[y:y+EFFECT_SIZE, x:x+EFFECT_SIZE]
        max_res = 0.0
        max_name = ''
        for effect_name, templates in EFFECT_TEMPLATES.items():
            for i in range(len(templates)):
                template = templates[i]
                mask = EFFECT_MASKS[effect_name][i]
                # print(test_image.shape, template.shape, mask.shape)
                res = cv2.matchTemplate(test_image, template, cv2.TM_CCOEFF_NORMED, mask=mask)
                res[np.isinf(res)] = 0
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if max_val > max_res:
                    max_res = max_val
                    max_name = effect_name
        results.append((max_name, max_res))
    # conbine the effects with the same 
    effects = [(name, round(val, 5)) for name, val in sorted(results, key=lambda x: x[1], reverse=True)]
    effects = [(name, max([val for n, val in effects if n == name])) for name, val in effects]
    effects = list(set(effects))
    # print(effects[:10])
    effects_name = [name for name, val in effects if val > threshold]
    return effects_name


cd_img = cv2.imread(CD_TEMPLATE_PATH, EFFECT_IMREAD_FLAG)
h, w = cd_img.shape[:2]
h, w = int(h * 900 / 1080), int(w * 900 / 1080)
# h, w = int(h * image_w / 1080), int(w * image_w / 1080)
cd_img = cv2.resize(cd_img, (w, h), interpolation=cv2.INTER_AREA)
# print('cd_image.shape:', cd_image.shape)
cd_mask = cd_img[:, :, 3]
cd_img = cd_img[:, :, :3]


@timeit
def read_effects(image: MatLike) -> list[str]:
    """
    Read the effects from the image.
    Image should be a 3-channel image and will not be modified.
    """

    assert image is not None, 'Cannot read image'
    assert image.shape[2] == 3, 'Incorrect image shape'

    if not EFFECT_TEMPLATES:
        read_effect_templates()
    
    image = image.copy()

    # resize the image to 900 width
    image_h, image_w = image.shape[:2]
    w, h = 900, int(image_h * 900 / image_w)
    image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)

    res = cv2.matchTemplate(image, cd_img, cv2.TM_CCOEFF_NORMED, mask=cd_mask)
    res[np.isinf(res)] = 0
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    max_locs = np.where(res >= [0.9])

    # remove the locations that are too close to edge
    max_locs_ = []
    for i in range(len(max_locs[0])):
        if max_locs[0][i] < 30 or max_locs[0][i] > w - 30 or max_locs[1][i] < 30 or max_locs[1][i] > h - 30:
            continue
        max_locs_.append((max_locs[0][i], max_locs[1][i]))
    # print(f'{max_locs_=}, {max_val=} at {max_loc=}')
    # print(res >= [0.8])
    
    # for pt in zip(*max_locs):
    #     cv2.rectangle(image, pt, (pt[0] + EFFECT_SIZE + 10, pt[1] + int(image_h * 900 / 5. / image_w)), (0, 0, 255), 2)
    
    # for x, y in zip(max_locs_[0], max_locs_[1]):
    #     cv2.rectangle(image, (x, y), (x + EFFECT_SIZE + 10, y + int(image_h * 900 / 5. / image_w)), (0, 0, 255), 2)

    # print(f'{max_locs=}, {max_locs_=}, {max_val=} at {max_loc=}')
    # resize the image to 0.5 times the original size
    # image_test = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    # res_test = cv2.resize(res, (0, 0), fx=0.5, fy=0.5)
    # cv2.imshow('image', image_test)
    # cv2.imshow('res', res_test)
    # # cv2.imshow('cd', cd_image)
    # # cv2.imshow('res', res)
    # cv2.waitKey(0)

    # convert max_locs to a list of tuples
    # max_locs: list[tuple[int, int]] = list(zip(max_locs_[1], max_locs_[0]))
    max_locs = max_locs_

    # remove all the locations that are too close to each other, keep the one with the highest value
    max_locs = sorted(max_locs, key=lambda x: res[x[1], x[0]], reverse=True)
    for i in range(len(max_locs)):
        for j in range(i+1, len(max_locs)):
            if abs(max_locs[i][0] - max_locs[j][0]) < 2 and abs(max_locs[i][1] - max_locs[j][1]) < 2:
                if res[max_locs[i][1], max_locs[i][0]] > res[max_locs[j][1], max_locs[j][0]]:
                    max_locs[j] = (-1, -1)
                else:
                    max_locs[i] = (-1, -1)
    max_locs = [loc for loc in max_locs if loc != (-1, -1)]
    
    # print(max_val)
    # print(max_loc)
    # cv2.imshow('image', image)
    # cv2.imshow('cd', cd_image)
    # cv2.imshow('mask', mask)
    # cv2.imshow('res', res)
    # cv2.waitKey(0)

    image_list: list[MatLike] = []

    if max_val > 0.8:
        # print('CD found')
        for max_loc in max_locs:
            # print(max_loc)
            top_left = max_loc[0] - 5, max_loc[1]
            bottom_right = (top_left[0] + EFFECT_SIZE + 10, top_left[1] + int(image_h * 900 / 5. / image_w))
            image_ = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            image_list.append(image_)
    else:
        print('CD not found')
        # image_list.append(image)
        
    results = []
    for image_ in image_list:
        # print('image_.shape:', image_.shape)
        # cv2.imshow('image_', image_)
        # cv2.waitKey(0)
        result = read_effect(image_, 0.8)
        # print('scale_result:', read_effect_scale(image_, 0.8))
        # print(result)
        for effect in result:
            results.append(effect)
    results = list(set(results))
    # print(results)
    return results


 

def gen_board_setting(effects: list[str]) -> SettingType:

    if not to_setting:
        set_toSetting()

    results = {}
    for effect in effects:
        if effect in to_setting:
            setting = to_setting[effect]
            if setting:
                for key, values in setting.items():
                    if key not in results:
                        results[key] = values
                    else:
                        results[key].extend(values)
                        results[key] = list(set(results[key]))
                # results.update(setting)

    return results



if __name__ == '__main__':

    file_path = R"screenshots\Screenshot_20240323-012256.png"
    # file_path = R"E:/Screenshot_2024-03-26-21-55-09-64_d05ce97d19cf4f15bd3a34cdb85fe924.jpg"
    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    results = read_effects(image)
    print(f"{results:}")
    setting = gen_board_setting(results)
    print(f"{setting:}")
