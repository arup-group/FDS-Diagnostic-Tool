# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:54:01 2019

@author: javor
"""

import b673.scraping_fxn as scr
import pandas as pd
import time
import json
import os


def setup_analysis(config):
    """Creates save locations and defines analysis setup as per config file"""

    # Valid analysis setup for this version build
    PER_CYCLE_SETUP = ['ts', 'press_itr', 'vel_err', 'cycles', 'press_err']
    PER_MESH_SETUP = ['max_div', 'min_div', 'vn', 'cfl', 'lagr', 'hrr', 'nrg_loss']

    PER_CYCLE_CONSTANTS = ['sim_time', 'log_time']

    per_mesh_info = {}
    per_cycle_info = {}

    per_mesh_info['dict'] = {}
    per_mesh_info['lst'] = {}
    per_mesh_info['fx'] = []
    per_cycle_info['dict'] = {}
    per_cycle_info['lst'] = []
    per_cycle_info['fx'] = []

    # Proj info is core and no further configurations are proposed for this stage
    sim_info = dict.fromkeys(['ver', 'date_start', 'sim_end', 'cores_n', 'tot_elp_time', 'stop_cond'])

    # Add per cycle constants

    for j in PER_CYCLE_CONSTANTS:
        per_cycle_info['fx'].append(j)
        per_cycle_info['dict'][j] = None

    # Setup save structure as per each configuration

    for j in config['log_data']:

        if config['log_data'][j] and j in PER_CYCLE_SETUP:
            per_cycle_info['fx'].append(j)
            per_cycle_info['dict'][j] = None

        if config['log_data'][j] and j in PER_MESH_SETUP:
            per_mesh_info['fx'].append(j)
            if j == 'cpu_step':
                per_mesh_info['dict']['cpu_step'] = {}
                per_mesh_info['lst']['cpu_step'] = []
                per_mesh_info['dict']['cpu_tot'] = {}
                per_mesh_info['lst']['cpu_tot'] = []
            else:
                per_mesh_info['dict'][j] = {}
                per_mesh_info['lst'][j] = []

    return sim_info, per_mesh_info, per_cycle_info

def get_data(outfile_file_path, output_loc, config, mesh_data):

    start_time = time.time()

    sim_info, per_mesh_info, per_cycle_info = setup_analysis(config)

    # This is used to fill at every cycle turn
    per_cycle_dict = per_cycle_info['dict'].copy()

    # Mesh setup
    cycle_check = {}
    current_mesh = None
    mesh_line = None
    success_scrapping = False


    with open(outfile_file_path, "r") as file:
        for j, line in enumerate(file):

            # Populate data dict
            sim_info_fx_to_use = [key for key in sim_info.keys() if sim_info[key] is None]
            for fx in sim_info_fx_to_use:
                scr.scrape(fx, line, sim_info)

            # Populate mesh dicts
            scr.scrape('itr_date', line, cycle_check)

            if 'cycles' in cycle_check:

                for i in per_mesh_info['dict']:
                    if per_mesh_info['dict'][i] != {}:
                        per_mesh_info['lst'][i].append(per_mesh_info['dict'][i])
                        per_mesh_info['dict'][i] = {}

                if all(value is not None for value in per_cycle_dict.values()):
                    per_cycle_info['lst'].append(per_cycle_dict)
                    per_cycle_dict = per_cycle_info['dict'].copy()

                cycle_check = {}

            # Get per cycle data
            cycle_fx_to_use = [key for key in per_cycle_dict.keys() if per_cycle_dict[key] is None]
            for fx in cycle_fx_to_use:
                scr.scrape(fx, line, per_cycle_dict, mesh_info=mesh_data['mesh_info'])

            current_mesh, mesh_line = scr.mesh_n(line, current_mesh, mesh_line)

            # Get per mesh data

            if current_mesh is not None:
                m_line_str = str(mesh_line)

                if m_line_str in scr.per_mesh_run_order.keys():
                    # print('here')
                    for fx in scr.per_mesh_run_order[m_line_str]:
                        if fx in per_mesh_info['fx']:
                            success_scrapping = scr.scrape_succs(fx, line, per_mesh_info['dict'], success_scrapping,
                                                            n_mesh=current_mesh, mesh_info=mesh_data['mesh_info'])

                        if success_scrapping:
                            break

                mesh_line = mesh_line + 1


    # Save requested data
    per_cycle_info['lst'].append(per_cycle_dict)
    per_cycle_info['lst'] = pd.DataFrame(per_cycle_info['lst'])
    per_cycle_info['lst'].to_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), index=False)

    for i in per_mesh_info['dict']:
        per_mesh_info['lst'][i].append(per_mesh_info['dict'][i])
        per_mesh_info['lst'][i] = pd.DataFrame(per_mesh_info['lst'][i])
        per_mesh_info['lst'][i]['sim_time'] = per_cycle_info['lst']['sim_time']
        per_mesh_info['lst'][i]['log_time'] = per_cycle_info['lst']['log_time']
        per_mesh_info['lst'][i].to_csv(os.path.join(output_loc, 'data', f'{i}.csv'), index=False)

    sim_info['date_start'] = sim_info['date_start'].strftime("%B %d, %Y %H:%M:%S")
    with open(os.path.join(output_loc, 'data', 'sim_info.json'), 'w') as fp:
        json.dump(sim_info, fp, indent=4)

    # Get some information for logging
    dt = time.time() - start_time
    data_sizes = {k : per_mesh_info['lst'][k].shape for k in per_mesh_info['lst']}
    data_sizes['cycle_info'] = per_cycle_info['lst'].shape

    print(f'Time : {dt:.2f} Output: {data_sizes}')
