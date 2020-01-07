import json
import os

YEAR = '16'
SEM = 'sem6'
OUT_DIR = os.path.join('data', 'output', 'results', YEAR, SEM)
OUT_DIR_PD = os.path.join('data', 'output', 'pd', YEAR, SEM)

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

with open('data/inputs/reg_list.json') as f:
    reg_list = json.load(f)
    bce_reg_list = [reg for reg in reg_list[YEAR] if reg[5:8] == '126']

with open('data/inputs/result_links.json') as f:
    result_links = json.load(f)
    base_link = result_links[YEAR][SEM]
