import os
import glob
import re
import pandas as pd
import json
import logging
import sys


class simInfo:


    def __init__(self):
        pass

    def setup_logger(self):
        pass

    def gets_locations(self):
        pass

    def create_folders(self):

    def loads_configurations(self):
        pass

    def gets_version(self):
        pass



def prcs_submit_file(submit_file):
    """Creates dict of running queue  file """

    submit_data = {}
    with open(submit_file) as f:
        for line in f:
            try:
                line = line.rstrip()
                line = line.replace('"', '')
                path = os.path.normpath(line)
                path_parts = path.split(os.sep)
                submit_data['{}_{}'.format(path_parts[-2], path_parts[-1])] = path
            except IndexError:
                pass

    return submit_data


def create_diag_dirs(full_output_loc):
    """"Creates appropriate subfolders"""
    subfolders = ['logs', 'data', 'imgs', 'inf']

    for subf in subfolders:
        os.makedirs(os.path.join(full_output_loc, subf), exist_ok=True)


def get_inpt_files_loc(sim_loc):
    '''Gets the location of the fds and out files'''

    sim_files_loc = {}

    fds_files = glob.glob(os.path.join(sim_loc, '*.fds'))
    if len(fds_files) == 1:
        sim_files_loc['fds_f_loc'] = fds_files[0]
    else:
        raise Exception('Multiple or no *.fds files')

    out_files = glob.glob(os.path.join(sim_loc, '*.out'))
    if len(out_files) == 1:
        sim_files_loc['out_f_loc'] = out_files[0]
    else:
        raise Exception('Multiple or no *.out files')

    return sim_files_loc


def create_runtime_dict(sim_loc):
    runtime_dict = {'ver': None,
                    'f_out_loc': None,
                    'f_fds_loc': None,
                    'is_imgs': False,
                    'is_mesh_info': False,
                    'ís_sprkl_info': False,
                    'is_extr_info': False}

    fds_files = glob.glob(os.path.join(sim_loc, '*.fds'))
    if len(fds_files) == 1:
        runtime_dict['f_fds_loc'] = fds_files[0]
    else:
        raise Exception('Multiple or no *.fds files')

    out_files = glob.glob(os.path.join(sim_loc, '*.out'))
    if len(out_files) == 1:
        runtime_dict['f_out_loc'] = out_files[0]
    else:
        raise Exception('Multiple or no *.out files')

    return runtime_dict

    return runtime_dict



def get_version(filepath):
    ver_ptn = r'(?:[Vv]ersion|[Rr]evision)[\s:A-Za-z]+(\d+\.\d+\.\d+)'

    with open(filepath, "r", errors='ignore') as file:
        for line in file:
            search_result = re.search(ver_ptn, line)
            if search_result is not None:
                ver = search_result.group(1)
                return ver

def load_results(output_loc):
    """Utility function that loads all results from the"""

    loaded_res = {}

    csv_files = glob.glob(os.path.join(output_loc, '*.csv'))
    for file in csv_files:
        base = os.path.basename(file)
        loaded_res[os.path.splitext(base)[0]] = pd.read_csv(file)

    json_files = glob.glob(os.path.join(output_loc, '*.json'))
    for file in json_files:
        base = os.path.basename(file)
        with open(file) as f:
            loaded_res[os.path.splitext(base)[0]] = json.load(f)

    return loaded_res

def check_data_avaliability(output_loc):
    "Checks the currently avaliable data before plotting"

    files_check = {}
    data_files ={'cfl': 'data/cfl.csv',
                 'cycle_info' : 'data/cycle_info.csv',
                 'hrr': 'data/hrr.csv',
                 'lagr': 'data/lagr.csv',
                 'max_div': 'data/max_div.csv',
                 'min_div': 'data/min_div.csv',
                 'vn': 'data/vn.csv',
                 'nrg_loss': 'data/nrg_loss.csv',
                 'mesh_data': 'data/mesh_data.json',
                 'sim_info': 'data/sim_info.json',
                 'img_xy': 'imgs/xy.png'}

    for file in data_files:
        if os.path.isfile(os.path.join(output_loc, data_files[file])):
            files_check[file] = True
        else:
            files_check[file] = False

    return files_check


def setup_logger(logger_name, log_file, level=logging.INFO):

    format = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    l = logging.getLogger(logger_name)
    if l.hasHandlers():
        l.handlers.clear()
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(format)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(format)

    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)
    l.propagate = False

    return l
