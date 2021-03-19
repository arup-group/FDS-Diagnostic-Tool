# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 23:40:49 2019

@author: javor
"""


def tot_el(out_dict):
    '''Calculates total elements from scraped mesh info'''

    from functools import reduce

    out_dict['tot_el'] = 0

    for key in out_dict['mesh_info'].keys():
        mesh_el_sum = reduce((lambda x, y: x * y), out_dict['mesh_info'][key][0:3])
        out_dict['mesh_info'][key] += [mesh_el_sum]
        out_dict['tot_el'] += mesh_el_sum

    return out_dict


def tot_volume(out_dict):
    '''Calculates total volume of model in m3'''

    out_dict['tot_volume'] = 0

    for mesh in out_dict['mesh_info']:
        mesh_list = out_dict['mesh_info'][mesh]
        out_dict['tot_volume'] += (mesh_list[4] - mesh_list[3]) * (mesh_list[6] - mesh_list[5]) * (
                    mesh_list[8] - mesh_list[7])

    return out_dict


def model_range(out_dict):
    '''Calculates total volume of model in m3'''

    out_dict['range'] = {'xmin': 100000,
                         'xmax': -100000,
                         'ymin': 100000,
                         'ymax': -100000,
                         'zmin': 100000,
                         'zmax': -100000}

    for mesh in out_dict['mesh_info']:

        mesh_list = out_dict['mesh_info'][mesh]

        if mesh_list[3] < out_dict['range']['xmin']:
            out_dict['range']['xmin'] = mesh_list[3]

        if mesh_list[4] > out_dict['range']['xmax']:
            out_dict['range']['xmax'] = mesh_list[4]

        if mesh_list[5] < out_dict['range']['ymin']:
            out_dict['range']['ymin'] = mesh_list[5]

        if mesh_list[6] > out_dict['range']['ymax']:
            out_dict['range']['ymax'] = mesh_list[6]

        if mesh_list[7] < out_dict['range']['zmin']:
            out_dict['range']['zmin'] = mesh_list[7]

        if mesh_list[8] > out_dict['range']['zmax']:
            out_dict['range']['zmax'] = mesh_list[8]

    return out_dict


def grid_size(out_dict):
    '''Calculates the grid size for each mesh'''

    mesh_sizes = {}

    for key in out_dict['mesh_info'].keys():
        mesh_sizes[key] = round((out_dict['mesh_info'][key][4] -
                                 out_dict['mesh_info'][key][3]) / out_dict['mesh_info'][key][0], 2)

    out_dict['grid_size'] = mesh_sizes

    return out_dict


def calc_loc(mesh_loc, mesh_info, n_mesh):
    coord_loc = [-1, -1, -1]

    name = 'mesh_{}'.format(n_mesh)
    coord_loc[0] = round(
        (mesh_info[name][4] - mesh_info[name][3]) * mesh_loc[0] / mesh_info[name][0] + mesh_info[name][3], 1)
    coord_loc[1] = round(
        (mesh_info[name][6] - mesh_info[name][5]) * mesh_loc[1] / mesh_info[name][1] + mesh_info[name][5], 1)
    coord_loc[2] = round(
        (mesh_info[name][8] - mesh_info[name][7]) * mesh_loc[2] / mesh_info[name][2] + mesh_info[name][7], 1)

    return coord_loc


def scrape_obst(fds_filepath, n, fudge=0, enforce_grid=True):
    '''Reads an FDS input file an scrapes the location of all obsticles discetising in a uniform grid defined
    by the coordinates of each grid cell.
    
    Input parameters:
        fds_filepath (str) : absolute filepath to the fds file
        n (int) : size of the grid
        fudge (float) : shifts the coordinate of each grid cell centre by a specified value in all directions
        enforce_grid(bool) : snaps all obstruction to the defined grid
        
    Returns:
        obst_pd (pandas dataframe): a dataframe containing the x,y,z location of all scrapped grid cells'''

    import numpy as np
    import re
    import pandas as pd

    mesh_pattern = r"&OBST ID='[\s\w]+', XB\s*=\s*((?:(?:[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)[\s,]*?){6})"
    obst_lst = list()

    count = 0

    with open(fds_filepath, "r") as file:
        for line in file:
            result = re.search(mesh_pattern, line)

            if result is not None:
                count += 1
                test = [float(i) for i in re.split(',', result.group(1))]
                x_lst = np.arange(min(test[0] + fudge, test[1] + fudge), max(test[0] + fudge, test[1] + fudge),
                                  n).tolist()
                y_lst = np.arange(min(test[2] + fudge, test[3] + fudge), max(test[2] + fudge, test[3] + fudge),
                                  n).tolist()
                z_lst = np.arange(min(test[4] + fudge, test[5] + fudge), max(test[4] + fudge, test[5] + fudge),
                                  n).tolist()

                obst_dict = [{'x': round(x, 1), 'y': round(y, 1), 'z': round(z, 1)} for x in x_lst for y in y_lst for z
                             in z_lst]
                obst_lst.append(obst_dict)

    flattened = [val for sublist in obst_lst for val in sublist]
    obst_pd = pd.DataFrame(flattened).drop_duplicates()

    if enforce_grid == True:
        obst_pd['x'] = obst_pd['x'] - (obst_pd['x'] * 10 % (10 * n)) / 10
        obst_pd['y'] = obst_pd['y'] - (obst_pd['y'] * 10 % (10 * n)) / 10
        obst_pd['z'] = obst_pd['z'] - (obst_pd['z'] * 10 % (10 * n)) / 10

    return obst_pd

def test():
    print('TEST')