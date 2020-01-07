import argparse
import os
import json


class Params:
    parser = argparse.ArgumentParser()

    parser.add_argument('--delay', default=900, type=int, help='Enter sleep time for tracker.')
    parser.add_argument('--debug', default=True, type=bool)
    parser.add_argument('--n_process', default=5, type=int)
    parser.add_argument('--YEAR', help='ex: 16, 17, 18, 19')
    parser.add_argument('--SEM', help='ex: sem1, sem2... sem8')

    # parser.add_argument('--OUT_DIR',
    #                     default=os.path.join('data', 'output', 'results', parser.YEAR, parser.SEM))
    # YEAR = '16'
    # SEM = 'sem6'
    # OUT_DIR = os.path.join('data', 'output', 'results', YEAR, SEM)
    # OUT_DIR_PD = os.path.join('data', 'output', 'pd', YEAR, SEM)


def get_reg_list(YEAR):
    with open('data/inputs/reg_list.json') as f:
        reg_json = json.load(f)
    return reg_json[YEAR]


def get_bce_reg_list(YEAR):
    reg_list = get_reg_list(YEAR)
    bce_reg_list = [reg for reg in reg_list if reg[5:8] == '126']
    return bce_reg_list
