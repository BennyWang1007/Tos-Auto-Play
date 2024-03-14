import cv2
import numpy as np
import os
from constant import *

def gen_templates() -> None:
    """
    Generate templates for the board recognition.
    """

    assert os.path.exists(TEMPLATE_128_PATH), f'Path {TEMPLATE_128_PATH} does not exist'

    if not os.path.exists(TEMPLATE_SAVE_PATH):
        os.makedirs(TEMPLATE_SAVE_PATH)

    if not os.path.exists(FINAL_TEMPLATE_PATH):
        os.makedirs(FINAL_TEMPLATE_PATH)
    
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

            # x1, x2 = int(RUNE_SIZE * 0.6), int(RUNE_SIZE * 0.6) + extra_image.shape[1]
            # x2 = min(x2, RUNE_SIZE)
            # y1, y2 = 0, extra_image.shape[0]

            # alpha_s = extra_image[:, :, 3] / 255.0
            # alpha_l = 1.0 - alpha_s

            # for c in range(0, 3):
            #     for x in range(x1, x2):
            #         for y in range(y1, y2):
            #             template[y, x, c] = (alpha_s[y - y1, x - x1] * extra_image[y - y1, x - x1, c] +
            #                                 alpha_l[y - y1, x - x1] * template[y, x, c])
                        
            # no_extension = file.split('.')[0]
            # cv2.imwrite(TEMPLATE_SAVE_PATH + no_extension + '_e.png', template)

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
                    elif overlay_file == "Chen.png": suffix = "Chen"
                    elif overlay_file == "BunBlackChess.png": suffix = "BChess"
                    elif overlay_file == "BunWhiteChess.png": suffix = "WChess"
                    elif overlay_file == "ShieldGem.png": suffix = "s"
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

    print(f'{generate_count} templates generated.')
                    

if __name__ == '__main__':
    gen_templates()