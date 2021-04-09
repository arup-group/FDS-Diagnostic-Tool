import os
import glob
import re
import pandas as pd
import json


def prcs_submit_file(submit_file):
    """Creates dict of running queue  file """

    submit_data = {}
    with open(submit_file) as f:
        for line in f:
            line = line.rstrip()
            path = os.path.normpath(line)
            path_parts = path.split(os.sep)
            submit_data['{}_{}'.format(path_parts[-2], path_parts[-1])] = path

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
    ver_ptn = r'(?:[Vv]ersion|[Rr]evision)[\s:]+(.+)'

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


