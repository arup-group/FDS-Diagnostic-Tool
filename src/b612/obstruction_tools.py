import time
import json
import pandas as pd
import numpy as np
import re
from PIL import Image, ImageOps
import os
import itertools

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



    mesh_pattern = r"&OBST ID='[\s\w\[\]]+',\s*XB\s*=\s*((?:(?:[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)[\s,]*?){6})"
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

                combined = [x_lst, y_lst, z_lst]
                itr_comb = list(itertools.product(*combined))
                obst_lst.append(itr_comb)

    flattened = [val for sublist in obst_lst for val in sublist]
    obst_pd = pd.DataFrame(flattened,  columns=['x', 'y', 'z'])
    obst_pd = obst_pd.round(1)
    obst_pd = obst_pd.drop_duplicates()

    if enforce_grid == True:
        obst_pd['x'] = (obst_pd['x'] - (obst_pd['x'] * 10 % (10 * n)) / 10)
        obst_pd['y'] = (obst_pd['y'] - (obst_pd['y'] * 10 % (10 * n)) / 10)
        obst_pd['z'] = (obst_pd['z'] - (obst_pd['z'] * 10 % (10 * n)) / 10)

    return obst_pd


def calc_obstr_volume(obst_info, n, mesh_data, save_path):

    mesh_data['obst_vol'] = len(obst_info.index)*n**3
    mesh_data['air_vol'] = mesh_data['tot_vol'] - mesh_data['obst_vol']
    mesh_data['obst_discr'] = n

    #Save location
    with open(os.path.join(save_path, 'data', 'mesh_data.json'), 'w') as f:
        json.dump(mesh_data, f, indent=4)

    return mesh_data


def fingerprint_single(data_dict, save_path, obst_pd, n, vp):

    """Creates image of geometry for xy, yz, xz views.
    Principle of operation - Samples mesh domain and obstruction to uniform grid with size n.
    Calculates N obstructions / N grids for xy, yz and xz direction.
    Converts array to image where darker parts show higher density of obstructions
    """

    dirs = {'xz': {'w': ['x_min', 'x_max', 'x'], 'h': ['z_min', 'z_max', 'z'], 'norm': ['y_n']},
            'yz': {'w': ['y_min', 'y_max', 'y'], 'h': ['z_min', 'z_max', 'z'], 'norm': ['x_n']},
            'xy': {'w': ['x_min', 'x_max', 'x'], 'h': ['y_min', 'y_max', 'y'], 'norm': ['z_n']}}


    sizes_lst = list()
    size_dict = {}

    # Processing meshes. Meshes are snapped to a uniform grid

    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['x_n'] = int(round((mesh_list[4] - mesh_list[3]) / n, 0))
        size_dict['y_n'] = int(round((mesh_list[6] - mesh_list[5]) / n, 0))
        size_dict['z_n'] = int(round((mesh_list[8] - mesh_list[7]) / n, 0))
        size_dict['x_min'] = round(mesh_list[3] - (mesh_list[3]*10 % (10 * n)) / 10, 1)
        size_dict['y_min'] = round(mesh_list[5] - (mesh_list[5]*10 % (10 * n)) / 10, 1)
        size_dict['z_min'] = round(mesh_list[7] - (mesh_list[7]*10 % (10 * n)) / 10, 1)

        size_dict['x_max'] = round(size_dict['x_min'] + size_dict['x_n']*n, 1)
        size_dict['y_max'] = round(size_dict['y_min'] + size_dict['y_n']*n, 1)
        size_dict['z_max'] = round(size_dict['z_min'] + size_dict['z_n']*n, 1)

        sizes_lst.append(size_dict)
        size_dict = {}

    sizes_pd = pd.DataFrame(sizes_lst)
    width_dict = {}
    height_dict = {}

    #Determine the min and maximum width
    w_min = round(sizes_pd[dirs[vp]['w'][0]].min(), 1)
    w_max = round(sizes_pd[dirs[vp]['w'][1]].max(), 1)

    for k, j in enumerate(np.arange(w_min, w_max + 0.001, n), 0):

        name = str(round(j, 1))
        if name == '-0.0': name = '0.0'
        width_dict[name] = k

    for k, j in enumerate(
            np.round(np.arange(sizes_pd[dirs[vp]['h'][0]].min(), sizes_pd[dirs[vp]['h'][1]].max() + 0.001, n), 1)):

        name = str(round(j, 1))
        if name == '-0.0': name = '0.0'
        height_dict[str(j)] = k

    domain_size_np = np.zeros([len(height_dict), len(width_dict)])

    # TODO count each mesh aeparately and update them

    for i in sizes_lst:
        w1 = width_dict[str(i[dirs[vp]['w'][0]])]
        w2 = width_dict[str(i[dirs[vp]['w'][1]])]
        h1 = height_dict[str(i[dirs[vp]['h'][0]])]
        h2 = height_dict[str(i[dirs[vp]['h'][1]])]

        # TODO CHECK EDGES to avoid dublication
        domain_size_np[h1:(h2 + 1), w1:(w2 + 1)] += i[dirs[vp]['norm'][0]]

    #    create obstruction array mirroring the mesh array
    obst_dstr = np.zeros(np.shape(domain_size_np))
    obst_pd = obst_pd.round(1)
    obst_groups = obst_pd.groupby([dirs[vp]['h'][2]])

    for group in obst_groups.groups.keys():

        obst_set = obst_groups.get_group(group)[dirs[vp]['w'][2]].value_counts().sort_index()
        obst_set = obst_set.reset_index()
        obst_set = obst_set.rename(columns={'index': 'index_old'})
        list_obst_sets = np.split(obst_set, np.flatnonzero(np.diff(obst_set['index_old']).round(1) != n) + 1)
        for obst in list_obst_sets:
            #If requested obstruction is out of bounds for the mesh grid
            #Get the obstruction that is at the max or min bound

            try:
                obst = obst.reset_index(drop=True)
                h = height_dict[str(group)]
                try:
                    w1 = width_dict[str(obst['index_old'].iloc[0])]
                    w1_idx = 0
                except KeyError:
                    w1 = width_dict[str(w_min)]
                    w1_idx = obst[obst['index_old'] == w_min].index[0]

                try:
                    w2 = width_dict[str(obst['index_old'].iloc[-1])]
                    w2_idx = len(obst.index)
                except KeyError:
                    w2 = width_dict[str(w_max)] - 1
                    w2_idx = obst[obst['index_old'] == w_max].index[0]


                obst_dstr[h, w1:w2+1] += obst.iloc[w1_idx:w2_idx, 1]

            except KeyError:
                pass

    # Process as image
    img = np.divide(obst_dstr, domain_size_np, out=np.zeros_like(obst_dstr), where=domain_size_np != 0)
    img = 255 - img * 255
    img = Image.fromarray(img.astype(np.uint8))
    img = ImageOps.flip(img)
    img.save(os.path.join(save_path, 'imgs', f'{vp}.png'))

    return ImageOps.flip(img)


def get_discr_param(mesh_data):
    """Returns most common grid size as descr param"""

    grid_list = []
    for i in mesh_data['grid_size']:
        grid_list.append(mesh_data['grid_size'][i])

    return max(set(grid_list), key=grid_list.count)


def process_obstructions(output_path, fds_filepath):
    """Function for processing obstructions and saving imgs"""

    start_time = time.time()

    with open(os.path.join(output_path, 'data', 'mesh_data.json'), 'r') as fp:
        mesh_data = json.load(fp)
    n = get_discr_param(mesh_data)


    print(f'Processing obstructions with {n} discretisation parameter.')

    obst_data = scrape_obst(fds_filepath, n, fudge=0, enforce_grid=True)
    calc_obstr_volume(obst_data, n, mesh_data, output_path)

    print('Processing imgs.')
    for vp in ['xz', 'xy', 'yz']:
        fingerprint_single(mesh_data, output_path, obst_data, n, vp=vp)

    print(f'Obstructions processed in {(time.time()-start_time):.2f}s.')
    return