import re


def get_mesh_info(fds_filepath, out_dict):
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


def get_tot_els(out_dict):
    '''Calculates total elements from scraped mesh info'''

    from functools import reduce

    out_dict['tot_el'] = 0

    for key in out_dict['mesh_info'].keys():
        mesh_el_sum = reduce((lambda x, y: x * y), out_dict['mesh_info'][key][0:3])
        out_dict['mesh_info'][key] += [mesh_el_sum]
        out_dict['tot_el'] += mesh_el_sum

    return out_dict


def get_tot_volume(out_dict):
    '''Calculates total volume of model in m3'''

    out_dict['tot_vol'] = 0

    for mesh in out_dict['mesh_info']:
        mesh_list = out_dict['mesh_info'][mesh]
        out_dict['tot_vol'] += (mesh_list[4] - mesh_list[3]) * (mesh_list[6] - mesh_list[5]) * (
                mesh_list[8] - mesh_list[7])

    return out_dict


def get_model_range(out_dict):
    '''Calculates total volume of model in m3'''

    out_dict['range'] = {}
    xmin = 1000000
    xmax = -1000000
    ymin = 1000000
    ymax = -1000000
    zmin = 1000000
    zmax = -1000000

    for mesh in out_dict['mesh_info']:

        mesh_list = out_dict['mesh_info'][mesh]

        if mesh_list[3] < xmin:
            xmin = mesh_list[3]

        if mesh_list[4] > xmax:
            xmax = mesh_list[4]

        if mesh_list[5] < ymin:
            ymin = mesh_list[5]

        if mesh_list[6] > ymax:
            ymax = mesh_list[6]

        if mesh_list[7] < zmin:
            zmin = mesh_list[7]

        if mesh_list[8] > zmax:
            zmax = mesh_list[8]

        out_dict['range']['dx'] = xmax - xmin
        out_dict['range']['dy'] = ymax - ymin
        out_dict['range']['dz'] = zmax - zmin

    return out_dict


def get_grid_size(out_dict):
    '''Calculates the grid size for each mesh'''

    mesh_sizes = {}

    for key in out_dict['mesh_info'].keys():
        mesh_sizes[key] = round((out_dict['mesh_info'][key][4] -
                                 out_dict['mesh_info'][key][3]) / out_dict['mesh_info'][key][0], 2)

    out_dict['grid_size'] = mesh_sizes

    return out_dict


def mesh_als(fds_path):
    mesh_data = {}

    mesh_data = get_mesh_info(fds_path, mesh_data)
    mesh_data = get_tot_els(mesh_data)
    mesh_data = get_grid_size(mesh_data)
    mesh_data = get_tot_volume(mesh_data)
    mesh_data = get_model_range(mesh_data)

    return mesh_data
