import os

import numpy as np

from util.constant import SCREEN_WIDTH, DIR

EFFECT_SCALE = 0.5

EFFECT_SIZE = SCREEN_WIDTH // 20
EFFECT_TEMPLATE_SIZE = int(EFFECT_SIZE * EFFECT_SCALE)

EFFECT_PATH = os.path.join(DIR, f'templates/effect_64/')
FINAL_EFFECT_PATH = os.path.join(DIR, f'templates/effect_{EFFECT_TEMPLATE_SIZE}/')

# FINAL_EFFECT_PATH = f'E:/effect_{EFFECT_TEMPLATE_SIZE}/'

EFFECT_NAMES: dict[str, list[int]] = {
    '1F': [64], # 1 combo in 1st batch
    '2F': [65], # 2 combo in 1st batch
    '3F': [66], # 3 combo in 1st batch
    '4F': [67], # 4 combo in 1st batch
    '5F': [68], # 5 combo in 1st batch
    '6F': [69], # 6 combo in 1st 
    'NoWF': [47, 418, 776], # No water combo in 1st batch
    'NoFF': [46, 419, 777], # No fire combo in 1st batch
    'NoGF': [48, 420, 778], # No grass combo in 1st batch
    'NoLF': [49, 421, 779], # No light combo in 1st batch
    'NoDF': [50, 422, 780], # No dark combo in 1st batch
    'NoHF': [145, 423, 781], # No heart combo in 1st batch
    '拼圖': [51], # Puzzle
    '強化': [87], # Enhance
    'ELI_WFG': [92], # Water, Fire, Grass
    'ELI_LD': [93], # Light, Dark
    'ELI_WFGLD': [94], # Water, Fire, Grass, Light, Dark
    'ELI_FGLD': [187], # Fire, Grass, Light, Dark
    'ELI_L+D+': [189], # Light+, Dark+
    'ELI_W+F+G+L+D+': [190], # Water+, Fire+, Grass+, Light+, Dark+
    'ELI_W+F+G+': [191], # Water+, Fire+, Grass+
    'ELI_W+F+G+L+': [192], # Water+, Fire+, Grass+, Light+
    '黏腐': [195, 1121, 1187], # Sticky
    '凍結': [205], # Freeze
    'SAME_LD': [225], # Same Light, Dark
    'SAME_WG': [226], # Same Water, Grass
    '紅綠燈': [257], 
    '7F': [294], # 7 combo in 1st batch
    '8F': [295], # 8 combo in 1st batch
    '9F': [296], # 9 combo in 1st batch
    '10F': [297], # 10 combo in 1st batch
    '石化': [298], # Petrify
    'SAME_WFG': [370], # Same Water, Fire, Grass
    'SAME_WFGLD': [371], # Same Water, Fire, Grass, Light, Dark
    'SAME_GD': [398], # Same Grass, Dark
    'SAME_FH': [399], # Same Fire, Heart
    'SAME_LH': [425], # Same Light, Heart
    'SAME_WFGLH': [428], # Same Water, Fire, Grass, Light, Heart
    'SAME_WFGD': [429], # Same Water, Fire, Grass, Dark
    'ELI_FD': [454], # Fire, Dark
    'ELI_WFD': [455], # Water, Fire, Dark
    'ELI_WFGD': [456], # Water, Fire, Grass, Dark
    'SAME_FGLD': [497], # Same Fire, Grass, Light, Dark
    'Inv_Recovery': [533, 1130], # Inverse Recovery
    '首消種類抗性20%': [534], # 20% Damage Reduction
    '首消種類抗性25%': [535], # 50% Damage Reduction
    '首消種類抗性50%': [536], # 50% Damage Reduction
    'SAME_WD': [574], # Same Water, Dark
    'SAME_LDH': [575], # Same Light, Dark, Heart
    'SAME_FL': [576], # Same Fire, Light
    '5_SAME': [625], # 5 combo with same color TODO: Check this
    '5_DIFF': [626], # 5 combo with different color TODO: Check this
    'SAME_WLH': [639], # Same Water, Light, 
    'SAME_GDH': [640], # Same Grass, Dark, Heart
    'SAME_GL': [697], # Same Grass, Light
    'SAME_WF': [698], # Same Water, Fire
    'SAME_WL': [699], # Same Water, Light
    'SAME_WH': [700], # Same Water, Heart
    'SAME_FG': [701], # Same Fire, Grass
    'SAME_FD': [702], # Same Fire, Dark
    'SAME_GH': [703], # Same Grass, Heart
    'SAME_DH': [704], # Same Dark, Heart
    'SAME_WFL': [705], # Same Water, Fire, Light
    'SAME_WFD': [706], # Same Water, Fire, Dark
    'SAME_WFH': [707], # Same Water, Fire, Heart
    'SAME_WGL': [708], # Same Water, Grass, Light
    'SAME_WGD': [709], # Same Water, Grass, Dark
    'SAME_WGH': [710], # Same Water, Grass, Heart
    '屬性4C': [714], # >=4 combo with attribute runes
    '屬性5C': [715], # >=5 combo with attribute runes
    '屬性6C': [716], # >=6 combo with attribute runes
    '屬性7C': [717], # >=7 combo with attribute runes
    '屬性8C': [718], # >=8 combo with attribute runes
    '屬性9C': [719], # >=9 combo with attribute runes
    '屬性10C': [720], # >=10 combo with attribute runes
    '灼熱地形': [722], # Scorching Terrain
    '結界地形': [723], # Barrier Terrain
    'SAME_WLD': [726], # Same Water, Light, Dark
    'SAME_WDH': [727], # Same Water, Dark, Heart
    'SAME_FGL': [728], # Same Fire, Grass, Light
    'SAME_FGD': [729], # Same Fire, Grass, Dark
    'SAME_FGH': [730], # Same Fire, Grass, Heart
    'SAME_FLD': [731], # Same Fire, Light, Dark
    'SAME_FLH': [732], # Same Fire, Light, Heart
    'SAME_FDH': [733], # Same Fire, Dark, Heart
    'SAME_GLD': [734], # Same Grass, Light, Dark
    'SAME_GLH': [735], # Same Grass, Light, Heart
    'SAME_LDH': [737], # Same Light, Dark, Heart
    'SAME_WFGLDH': [738], # Same Water, Fire, Grass, Light, Dark, Heart
    'NoW_ZERO': [827], # No Water combo in 1st batch, otherwise deal 0 damage
    'NoF_ZERO': [828], # No Fire combo in 1st batch, otherwise deal 0 damage
    'NoG_ZERO': [829], # No Grass combo in 1st batch, otherwise deal 0 damage
    'NoL_ZERO': [830], # No Light combo in 1st batch, otherwise deal 0 damage
    'NoD_ZERO': [831], # No Dark combo in 1st batch, otherwise deal 0 damage
    'NoH_ZERO': [832], # No Heart combo in 1st batch, otherwise deal 0 damage
    'BOMB': [833], # Bomb
    'SAME_WFLD': [834], # Same Water, Fire, Light, Dark
    'SAME_WGLD': [835], # Same Water, Grass, Light, Dark
    '十字盾': [868], # Cross
    '消水增加抗性20%': [914], # eliminate water increase resistance 20%
    '消水增加抗性25%': [915], # eliminate water increase resistance 25%
    '消水增加抗性50%': [916], # eliminate water increase resistance 50%
    '消火增加抗性20%': [917], # eliminate fire increase resistance 20%
    '消火增加抗性25%': [918], # eliminate fire increase resistance 25%
    '消火增加抗性50%': [919], # eliminate fire increase resistance 50%
    '消木增加抗性20%': [920], # eliminate grass increase resistance 20%
    '消木增加抗性25%': [921], # eliminate grass increase resistance 25%
    '消木增加抗性50%': [922], # eliminate grass increase resistance 50%
    '消光增加抗性20%': [923], # eliminate light increase resistance 20%
    '消光增加抗性25%': [924], # eliminate light increase resistance 25%
    '消光增加抗性50%': [925], # eliminate light increase resistance 50%
    '消暗增加抗性20%': [926], # eliminate dark increase resistance 20%
    '消暗增加抗性25%': [927], # eliminate dark increase resistance 25%
    '消暗增加抗性50%': [928], # eliminate dark increase resistance 50%
    '消心增加抗性20%': [929], # eliminate heart increase resistance 20%
    '消心增加抗性25%': [930], # eliminate heart increase resistance 25%
    '消心增加抗性50%': [931], # eliminate heart increase resistance 50%
    '消水減少抗性10%': [932], # eliminate water decrease resistance 10%
    '消水減少抗性20%': [933], # eliminate water decrease resistance 20%
    '消水減少抗性25%': [934], # eliminate water decrease resistance 25%
    '消水減少抗性50%': [935], # eliminate water decrease resistance 50%
    '消火減少抗性10%': [936], # eliminate fire decrease resistance 10%
    '消火減少抗性20%': [937], # eliminate fire decrease resistance 20%
    '消火減少抗性25%': [938], # eliminate fire decrease resistance 25%
    '消火減少抗性50%': [939], # eliminate fire decrease resistance 50%
    '消木減少抗性10%': [940], # eliminate grass decrease resistance 10%
    '消木減少抗性20%': [941], # eliminate grass decrease resistance 20%
    '消木減少抗性25%': [942], # eliminate grass decrease resistance 25%
    '消木減少抗性50%': [943], # eliminate grass decrease resistance 50%
    '消光減少抗性10%': [944], # eliminate light decrease resistance 10%
    '消光減少抗性20%': [945], # eliminate light decrease resistance 20%
    '消光減少抗性25%': [946], # eliminate light decrease resistance 25%
    '消光減少抗性50%': [947], # eliminate light decrease resistance 50%
    '消暗減少抗性10%': [948], # eliminate dark decrease resistance 10%
    '消暗減少抗性20%': [949], # eliminate dark decrease resistance 20%
    '消暗減少抗性25%': [950], # eliminate dark decrease resistance 25%
    '消暗減少抗性50%': [951], # eliminate dark decrease resistance 50%
    '消心減少抗性10%': [952], # eliminate heart decrease resistance 10%
    '消心減少抗性20%': [953], # eliminate heart decrease resistance 20%
    '消心減少抗性25%': [954], # eliminate heart decrease resistance 25%
    '消心減少抗性50%': [955], # eliminate heart decrease resistance 50%
    '首消種類減少抗性20%': [964], # first combo decrease resistance 20%
    '首消種類減少抗性25%': [965], # first combo decrease resistance 25%
    '首消種類減少抗性50%': [966], # first combo decrease resistance 50%
    '首消種類減少抗性1%': [968], # first combo decrease resistance 1%
    '首消種類減少抗性2%': [969], # first combo decrease resistance 2%
    '首消種類減少抗性5%': [970], # first combo decrease resistance 5%
    '水十字盾': [986], # water cross shield
    '火十字盾': [987], # fire cross shield
    '木十字盾': [988], # grass cross shield
    '光十字盾': [989], # light cross shield
    '暗十字盾': [990], # dark cross shield
    # '攻前': [28, 1139] # no damage before he attacks
}

EFFECT_TEMPLATES: dict[str, list[np.ndarray]] = {}

EFFECT_MASKS: dict[str, list[np.ndarray]] = {}