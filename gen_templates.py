import cv2
import numpy as np
import os
from constant import *
from effect.constant import EFFECT_NAMES
from effect.read_effect import gen_templates_effect

def gen_templates() -> None:
    """
    Generate templates for the board recognition.
    """

    assert os.path.exists(TEMPLATE_128_PATH), f'Path {TEMPLATE_128_PATH} does not exist'

    if not os.path.exists(TEMPLATE_SAVE_PATH):
        os.makedirs(TEMPLATE_SAVE_PATH)

    if not os.path.exists(FINAL_TEMPLATE_PATH):
        os.makedirs(FINAL_TEMPLATE_PATH)

    if not os.path.exists(FINAL_TEMPLATE_PATH + 'race/'):
        os.makedirs(FINAL_TEMPLATE_PATH + 'race/')

    
    # extra_image = cv2.imread(TEMPLATE_128_PATH + 'extra.png', cv2.IMREAD_UNCHANGED)
    # size = (int(extra_image.shape[1] * 150 / RUNE_SIZE), int(extra_image.shape[0] * 150 / RUNE_SIZE))
    # extra_image = cv2.resize(extra_image, size)
        
    print('Generating templates...')
    generate_count = 0

    for file in os.listdir(TEMPLATE_128_PATH):
        if file.endswith('.png'):

            if file[0] not in ['w', 'f', 'p', 'l', 'd', 'h', 'q']:
                continue
            template = cv2.imread(TEMPLATE_128_PATH + file, cv2.IMREAD_UNCHANGED)
            template = cv2.resize(template, (RUNE_SIZE, RUNE_SIZE))
            cv2.imwrite(TEMPLATE_SAVE_PATH + file, template)

            cropped_template = template[OFFSET[1]:OFFSET2[1], OFFSET[0]:OFFSET2[0]]
            if not os.path.exists(FINAL_TEMPLATE_PATH + file):
                cv2.imwrite(FINAL_TEMPLATE_PATH + file, cropped_template)
            generate_count += 1

            no_extension = file.split('.')[0]
            found = False
            # remove iced
            for char in ['1', '2', '3']:
                if char in no_extension:
                    found = True
                    break
            if found: continue

            
            for overlay_file in os.listdir(TEMPLATE_128_PATH + 'extra/'):
                if overlay_file.endswith('.png'):
                    if overlay_file == "Lin.png": suffix = "Lin"
                    elif overlay_file == "Bell.png": suffix = "Bell"
                    elif overlay_file == "BunBlackChess.png": suffix = "BChess"
                    elif overlay_file == "BunWhiteChess.png": suffix = "WChess"
                    elif overlay_file == "ShieldGem.png": suffix = "s"
                    elif overlay_file == "Jujutsu.png": suffix = "Jujutsu"
                    elif overlay_file == "FireMark.png": suffix = "FireMark"
                    else: raise ValueError(f'Unknown file {overlay_file}')

                    overlayed_name = file.split('.')[0] + f'_{suffix}.png'
                    if os.path.exists(TEMPLATE_SAVE_PATH + overlayed_name):
                        template_new = cv2.imread(TEMPLATE_SAVE_PATH + overlayed_name, cv2.IMREAD_UNCHANGED)
                    else:
                        template_new = template.copy()
                        overlay = cv2.imread(TEMPLATE_128_PATH + 'extra/' + overlay_file, cv2.IMREAD_UNCHANGED)
                        overlay = cv2.resize(overlay, (RUNE_SIZE, RUNE_SIZE))
                        overlay_np = np.asarray(overlay, dtype=np.float32)
                        template_np = np.asarray(template, dtype=np.float32)
                        alpha_s = overlay_np[:, :, 3] / 255.0
                        alpha_l = 1.0 - alpha_s
                        for c in range(0, 3):
                            template_new[:, :, c] = (alpha_s * overlay_np[:, :, c] + alpha_l * template_np[:, :, c])
                        template_new[:, :, 3] = np.maximum(template_new[:, :, 3], overlay_np[:, :, 3])
                        if not os.path.exists(TEMPLATE_SAVE_PATH + overlayed_name):
                            cv2.imwrite(TEMPLATE_SAVE_PATH + overlayed_name, template_new)
                    template_new = template_new[OFFSET[1]:OFFSET2[1], OFFSET[0]:OFFSET2[0]]
                    if not os.path.exists(FINAL_TEMPLATE_PATH + overlayed_name):
                        cv2.imwrite(FINAL_TEMPLATE_PATH + overlayed_name, template_new)
                    generate_count += 1

    # generate races
    race_count = 0
    if not os.path.exists(FINAL_RACE_PATH):
        os.makedirs(FINAL_RACE_PATH)
    for file in os.listdir(RACE_TEMPLATE_PATH):
        if file.endswith('.png'):
            template = cv2.imread(f'{RACE_TEMPLATE_PATH}{file}', cv2.IMREAD_UNCHANGED)
            template = cv2.resize(template, (RACE_SIZE, RACE_SIZE))
            cv2.imwrite(f'{FINAL_RACE_PATH}{file}', template)
            race_count += 1

    print(f'{generate_count} templates generated.')
    print(f'{race_count} races generated.')

# original_effect_path = R"C:\Users\benny\Desktop\tos_assets\export_fianl\ICON"

# def gen_ori_templates_effect():
#     for effect_name, effect_ids in EFFECT_NAMES.items():
#         for effect_id in effect_ids:
#             # fill the effect id to 3 digits with 0
#             effect_id = str(effect_id).zfill(3)
#             # template = cv2.imread(f'./templates/effects/{effect_id}.png', cv2.IMREAD_GRAYSCALE)
#             if not os.path.exists(EFFECT_PATH):
#                 os.makedirs(EFFECT_PATH)
#             template = cv2.imread(f'{original_effect_path}/ICON{effect_id}.png', cv2.IMREAD_UNCHANGED)
#             cv2.imwrite(f'{EFFECT_PATH}ICON{effect_id}.png', template)
    


                    

if __name__ == '__main__':
    gen_templates()
    gen_templates_effect()