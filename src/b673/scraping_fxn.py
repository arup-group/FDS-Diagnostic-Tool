# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 17:01:01 2019

@author: javor
"""

import re
import datetime
from b673.analysis_fxn import calc_loc


def ver(input_str, out_dict):
    pattern = r'(?:[Vv]ersion|[Rr]evision)[\s:]+(.+)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['ver'] = result.group(1)

    return out_dict

def chid(input_str, out_dict):
    pattern = r'ID\s[Ss]tring\s+:\s+(.+)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['chid'] = result.group(1)

    return out_dict

def stop_cond(input_str, out_dict):

    if 'completed successfully' in input_str:
        out_dict['stop_cond'] = 'completed'
    elif 'stopped by user' in input_str:
        out_dict['stop_cond'] = 'user'
    elif 'Numerical Instability' in input_str:
        out_dict['stop_cond'] = 'instability'
    return out_dict


    return out_dict

def sim_end(input_str, out_dict):
    pattern = r'[Ee]nd\s+[Tt]ime\s+\(s\)\s+(([-+]?[0-9]*\.?[0-9]+)([eE]([-+])?([0-9]+))?)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['sim_end'] = float(result.group(1))

    return out_dict


def date_start(input_str, out_dict):
    pattern = r'[A-Za-z]{3,}\s+\d+,\s+\d+\s+\d{2}:\d{2}:\d{2}'
    result = re.search(pattern, input_str)

    if result is not None:
        date_str = result.group(0)
        out_dict['date_start'] = datetime.datetime.strptime(date_str, "%B %d, %Y %H:%M:%S")

    return out_dict


def cores_n(input_str, out_dict):
    pattern = r'MPI\s+[Pp]rocesses:\s+([0-9]+)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['cores_n'] = int(result.group(1))

    return out_dict


def mesh_info(fds_filepath, out_dict):
    mesh_pattern = r'&MESH.+IJK\s*=\s*((?:(?:[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)[\s,]*?){3}).+XB\s*=\s*((?:(?:[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)[\s,]*?){6})'
    pattern_split = r'[\s,]+'
    mesh_dict = {}
    count = 0

    with open(fds_filepath, "r") as file:
        for line in file:
            result = re.search(mesh_pattern, line)

            if result is not None:
                count += 1

                mesh_size = [int(i) for i in re.split(pattern_split, result.group(1))]
                mesh_dim = [float(i) for i in re.split(pattern_split, result.group(2))]

                # TODO write it as dictionary of dictionaries
                mesh_dict['mesh_{}'.format(count)] = mesh_size + mesh_dim

    out_dict['mesh_info'] = mesh_dict
    return out_dict


def tot_elp_time(input_str, out_dict):
    pattern = r'[Ss]tepping.+:\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['tot_elp_time'] = round(float(result.group(1)))

    return out_dict


def itr_date(input_str, out_dict, **kwargs):
    pattern = r'[Tt]ime\s+[Ss]tep\s+(\d+)\s+([A-Za-z]{3,}\s+\d+,\s+\d+\s+\d{2}:\d{2}:\d{2})'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['cycles'] = int(result.group(1))
        date_str = result.group(2)
        out_dict['log_time'] = datetime.datetime.strptime(date_str, "%B %d, %Y %H:%M:%S")

    return out_dict


def log_time(input_str, out_dict, **kwargs):
    pattern = r'[Tt]ime\s+[Ss]tep\s+(\d+)\s+([A-Za-z]{3,}\s+\d+,\s+\d+\s+\d{2}:\d{2}:\d{2})'
    result = re.search(pattern, input_str)

    if result is not None:
        date_str = result.group(2)
        out_dict['log_time'] = datetime.datetime.strptime(date_str, "%B %d, %Y %H:%M:%S")

    return out_dict


def cycles(input_str, out_dict, **kwargs):
    pattern = r'[Tt]ime\s+[Ss]tep\s+(\d+)\s+([A-Za-z]{3,}\s+\d+,\s+\d+\s+\d{2}:\d{2}:\d{2})'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['cycles'] = int(result.group(1))

    return out_dict


def time_step(input_str, out_dict, **kwargs):
    pattern = r'[Ss]tep\s[Ss]ize:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['ts'] = float(result.group(1))

    return out_dict


def sim_time(input_str, out_dict, **kwargs):
    pattern = r'Total\s[Tt]ime:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['sim_time'] = float(result.group(1))

    return out_dict


def press_itr(input_str, out_dict, **kwargs):
    pattern = r'Iterations:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        out_dict['press_itr'] = int(result.group(1))

    return out_dict


def vel_err(input_str, out_dict, mesh_info=None, **kwargs):
    pattern = r'Velocity\sError:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-zA-Z\s]+\s+(\d+)[a-z\s]+\((?:\s+)?(\d+,?\s+\d+,?\s+\d+)'
    result = re.search(pattern, input_str)

    pattern_split = r'[\s,]+'

    if result is not None:
        out_dict['vel_err'] = float(result.group(1))
        m_num = int(result.group(2))
        out_dict['vel_err_m'] = f'm{m_num}'

        m_error_loc = [int(i) for i in re.split(pattern_split, result.group(3))]

        if mesh_info is not None:
            out_dict['vel_err_loc'] = calc_loc(m_error_loc, mesh_info, m_num)
        else:
            out_dict['vel_err_loc'] = m_error_loc

    return out_dict

def press_err(input_str, out_dict, mesh_info=None, **kwargs):
    pattern = r'Pressure\sError:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-zA-Z\s]+\s+(\d+)[a-z\s]+\((?:\s+)?(\d+,?\s+\d+,?\s+\d+)'
    result = re.search(pattern, input_str)

    pattern_split = r'[\s,]+'

    if result is not None:
        out_dict['press_err'] = float(result.group(1))
        m_num = int(result.group(2))
        out_dict['press_err_m'] = f'm{m_num}'

        m_error_loc = [int(i) for i in re.split(pattern_split, result.group(3))]

        if mesh_info is not None:
            out_dict['press_err_loc'] = calc_loc(m_error_loc, mesh_info, m_num)
        else:
            out_dict['press_err_loc'] = m_error_loc

    return out_dict


def mesh_n(input_str, n, mesh_line):
    pattern = r'^\s+Mesh\s+(\d+)$'
    result = re.search(pattern, input_str)

    if result is not None:
        n = int(result.group(1))
        mesh_line = 0

    return n, mesh_line


def cfl_n(input_str, out_dict, outcome, n_mesh, mesh_info=None, **kwargs):
    pattern = r'CFL number:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-z\s]+\((?:\s+)?(\d+,?(?:\s+)?\d+,?(?:\s+)?\d+)'
    pattern_split = r'[\s,]+'
    result = re.search(pattern, input_str)

    if result is not None:

        outcome = True
        cfl_loc = [int(i) for i in re.split(pattern_split, result.group(2))]
        out_dict['cfl']['m{}'.format(n_mesh)] = float(result.group(1))

        if mesh_info is not None:
            out_dict['cfl']['m{}_loc'.format(n_mesh)] = calc_loc(cfl_loc, mesh_info, n_mesh)
        else:
            out_dict['cfl']['m{}_loc'.format(n_mesh)] = cfl_loc

    else:
        outcome = False

    return out_dict, outcome


def max_div(input_str, out_dict, outcome, n_mesh, mesh_info=None, **kwargs):
    pattern = r'Max divergence:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-z\s]+\((?:\s+)?(\d+,?(?:\s+)?\d+,?(?:\s+)?\d+)'
    pattern_split = r'[\s,]+'
    result = re.search(pattern, input_str)

    if result is not None:

        outcome = True
        max_div_loc = [int(i) for i in re.split(pattern_split, result.group(2))]
        out_dict['max_div']['m{}'.format(n_mesh)] = float(result.group(1))

        if mesh_info is not None:
            out_dict['max_div']['m{}_loc'.format(n_mesh)] = calc_loc(max_div_loc, mesh_info, n_mesh)
        else:
            out_dict['max_div']['m{}_loc'.format(n_mesh)] = max_div_loc

    else:
        outcome = False

    return out_dict, outcome


def min_div(input_str, out_dict, outcome, n_mesh, mesh_info=None, **kwargs):
    pattern = r'Min divergence:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-z\s]+\((?:\s+)?(\d+,?(?:\s+)?\d+,?(?:\s+)?\d+)'
    pattern_split = r'[\s,]+'
    result = re.search(pattern, input_str)

    if result is not None:

        outcome = True
        min_div_loc = [int(i) for i in re.split(pattern_split, result.group(2))]
        out_dict['min_div']['m{}'.format(n_mesh)] = float(result.group(1))

        if mesh_info is not None:
            out_dict['min_div']['m{}_loc'.format(n_mesh)] = calc_loc(min_div_loc, mesh_info, n_mesh)
        else:
            out_dict['min_div']['m{}_loc'.format(n_mesh)] = min_div_loc

    else:
        outcome = False

    return out_dict, outcome


def loss_bound(input_str, out_dict, outcome, n_mesh, **kwargs):
    pattern = r'[Bb]oundaries:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        outcome = True
        out_dict['nrg_loss']['m{}'.format(n_mesh)] = float(result.group(1))
        out_dict['nrg_loss']['ctrl'] = 1

    else:
        out_dict['nrg_loss']['ctrl'] = 0
        outcome = False

    return out_dict, outcome


def hrr(input_str, out_dict, outcome, n_mesh, **kwargs):
    pattern = r'[Rr]ate:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        outcome = True
        out_dict['hrr']['m{}'.format(n_mesh)] = float(result.group(1))
        out_dict['hrr']['ctrl'] = 1

    else:
        out_dict['hrr']['ctrl'] = 0
        outcome = False

    return out_dict, outcome


def lagrange(input_str, out_dict, outcome, n_mesh, **kwargs):
    pattern = r'[Pp]articles:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)'
    result = re.search(pattern, input_str)

    if result is not None:
        outcome = True
        out_dict['lagr']['m{}'.format(n_mesh)] = float(result.group(1))
        out_dict['lagr']['ctrl'] = 1

    else:
        out_dict['lagr']['ctrl'] = 0
        outcome = False

    return out_dict, outcome


def vn_n(input_str, out_dict, outcome, n_mesh, mesh_info=None, **kwargs):
    pattern = r'VN\s+number:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-z\s]+\((?:\s+)?(\d+,?(?:\s+)?\d+,?(?:\s+)?\d+)'
    pattern_split = r'[\s,]+'
    result = re.search(pattern, input_str)

    if result is not None:

        outcome = True
        vn_loc = [int(i) for i in re.split(pattern_split, result.group(2))]
        out_dict['vn']['m{}'.format(n_mesh)] = float(result.group(1))

        if mesh_info is not None:
            out_dict['vn']['m{}_loc'.format(n_mesh)] = calc_loc(vn_loc, mesh_info, n_mesh)
        else:
            out_dict['vn']['m{}_loc'.format(n_mesh)] = vn_loc

    else:
        outcome = False

    return out_dict, outcome


def cpu_step(input_str, out_dict, outcome, n_mesh, **kwargs):
    pattern = r'CPU\/step:\s+((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)[a-zA-z,\s]+CPU:\s+([-+]?[0-9]*\.?[0-9]+)\s+(\w{1,3})'
    result = re.search(pattern, input_str)

    if result is not None:

        outcome = True
        out_dict['cpu_step']['m{}'.format(n_mesh)] = float(result.group(1))
        #        out_dict['cpu_tot_m{}'.format(n_mesh)] = float(result.group(2))

        if result.group(3) == 's':
            out_dict['cpu_tot']['m{}'.format(n_mesh)] = float(result.group(2))

        elif result.group(3) == 'min':
            out_dict['cpu_tot']['m{}'.format(n_mesh)] = float(result.group(2)) * 60

        elif result.group(3) == 'hr':
            out_dict['cpu_tot']['m{}'.format(n_mesh)] = float(result.group(2)) * 3600

    else:
        outcome = False

    return out_dict, outcome


basic_param = {
    'ver': ver,
    'chid': chid,
    'stop_cond' : stop_cond,
    'sim_end': sim_end,
    'date_start': date_start,
    'cores_n': cores_n,
    'tot_elp_time': tot_elp_time,
    'itr_date': itr_date,
    'ts': time_step,
    'sim_time': sim_time,
    'press_itr': press_itr,
    'vel_err': vel_err,
    'cfl': cfl_n,
    'max_div': max_div,
    'min_div': min_div,
    'nrg_loss': loss_bound,
    'hrr': hrr,
    'vn': vn_n,
    'cpu_step': cpu_step,
    'log_time': log_time,
    'cycles': cycles,
    'lagr': lagrange,
    'press_err': press_err}

per_mesh_run_order = {'1': ['cfl', 'max_div', 'min_div', 'vn', 'nrg_loss', 'hrr', 'lagr'],
                     '2': ['max_div', 'min_div', 'vn', 'nrg_loss', 'hrr', 'lagr', 'cfl'],
                     '3': ['min_div', 'cfl', 'max_div', 'vn', 'nrg_loss', 'hrr', 'lagr'],
                     '4': ['vn', 'cfl', 'max_div', 'min_div', 'nrg_loss', 'hrr', 'lagr'],
                     '5': ['lagr', 'hrr', 'nrg_loss', 'cfl', 'max_div', 'min_div', 'vn'],
                     '6': ['hrr', 'nrg_loss', 'cfl', 'max_div', 'min_div', 'vn', 'lagr'],
                     '7': ['nrg_loss', 'hrr', 'cfl', 'max_div', 'min_div', 'vn', 'lagr']}


def scrape(name, input_str, out_dict, **kwargs):
    out_dict = basic_param[name](input_str, out_dict, **kwargs)


def scrape_succs(name, input_str, out_dict, outcome, **kwargs):
    out_dict, outcome = basic_param[name](input_str, out_dict, outcome, **kwargs)
    return outcome


def scrape_m(name, input_str, out_dict, n_mesh):
    out_dict = basic_param[name](input_str, out_dict, n_mesh)
