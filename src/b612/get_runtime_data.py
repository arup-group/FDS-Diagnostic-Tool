# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:54:01 2019

@author: javor
"""

import scraping_fxn as scr
import pandas as pd
import time
import json
import os


def setup_analysis(config):
    '''Creates save locations and defines analysis setup as per config file '''

    # Valid analysis setup for this version build
    PER_CYCLE_SETUP = ['ts', 'press_itr', 'vel_err', 'cycles']
    PER_MESH_SETUP = ['max_div', 'min_div', 'vn', 'cfl', 'lagr', 'hrr', 'nrg_loss', 'cpu_step']

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
    sim_info = dict.fromkeys(['ver', 'date_start', 'sim_end', 'cores_n', 'tot_elp_time'])

    # Add per cycle constants

    for j in PER_CYCLE_CONSTANTS:
        per_cycle_info['fx'].append(j)
        per_cycle_info['dict'][j] = None


    # Setup save structure as per each configuration

    for j in config['log_data']:

        if config['log_data'][j] == True and j in PER_CYCLE_SETUP:
            per_cycle_info['fx'].append(j)
            per_cycle_info['dict'][j] = None

        if config['log_data'][j] == True and j in PER_MESH_SETUP:
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


start_time = time.time()

doc_file_path = r"C:\work\fds_tools\fds_diagnostics\docs\paisley\FC1_VO3\Fire_Scenario_1_VentOption3_Ru.out"
fds_file = r"C:\work\fds_tools\fds_diagnostics\docs\paisley\FC1_VO3\Fire_Scenario_1_VentOption3_Run1.fds"
mesh_data_file = r"C:\work\fds_tools\fds_diagnostics\tests\runtime_tests\data\mesh_data.json" # TODO REMOVE THIS
config_filepath = r"C:\work\fds_tools\fds_diagnostics\tests\runtime_tests\config.json" # TODO REMOVE THIS
output_loc = r'C:\work\fds_tools\fds_diagnostics\tests\runtime_tests'

# Load mesh data dict
with open(mesh_data_file) as f:
    mesh_data = json.load(f)

with open(config_filepath) as f:
    config = json.load(f)

# TODO add sim status feature for sim info
sim_info, per_mesh_info, per_cycle_info = setup_analysis(config)

# This is used to fill at every cycle turn
per_cycle_dict = per_cycle_info['dict']

# Mesh setup
cycle_check = {}

# ts_dict setup
# ts_dict = dict.fromkeys(['time_step', 'sim_time', 'press_itr', 'm_error', 'log_time', 'cycles'])
# ts_lst = list()

current_mesh = None
mesh_line = None
success_line = -1
i_max = 0

mesh_dicts = {'cfl_dict': {},
              'max_div_dict': {},
              'min_div_dict': {},
              'hrr_dict': {},
              'loss_dict': {},
              'vn_dict': {},
              'cpu_step_dict': {},
              'cpu_tot_dict': {},
              'lagrange_dict': {}}

cfl_lst = list()
max_div_lst = list()
min_div_lst = list()
hrr_lst = list()
loss_lst = list()
vn_lst = list()
cpu_step_lst = list()
cpu_tot_lst = list()
lagrange_lst = list()

i = 0




with open(doc_file_path, "r") as file:
    for line in file:

        # Populate data dict - KEEP
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

            if all(value != None for value in per_cycle_dict.values()):
                per_cycle_info['lst'].append(per_cycle_dict)
                per_cycle_dict = per_cycle_info['dict']

            # if mesh_dicts['cfl_dict'] != {}:
            #     cfl_lst.append(mesh_dicts['cfl_dict'])
            #     mesh_dicts['cfl_dict'] = {}
            #
            # if mesh_dicts['cpu_step_dict'] != {}:
            #     cpu_step_lst.append(mesh_dicts['cpu_step_dict'])
            #     mesh_dicts['cpu_step_dict'] = {}
            #
            # if mesh_dicts['cpu_tot_dict'] != {}:
            #     cpu_tot_lst.append(mesh_dicts['cpu_tot_dict'])
            #     mesh_dicts['cpu_tot_dict'] = {}
            #
            # if mesh_dicts['vn_dict'] != {}:
            #     vn_lst.append(mesh_dicts['vn_dict'])
            #     mesh_dicts['vn_dict'] = {}
            #
            # if mesh_dicts['max_div_dict'] != {}:
            #     max_div_lst.append(mesh_dicts['max_div_dict'])
            #     mesh_dicts['max_div_dict'] = {}
            #
            # if mesh_dicts['min_div_dict'] != {}:
            #     min_div_lst.append(mesh_dicts['min_div_dict'])
            #     mesh_dicts['min_div_dict'] = {}
            #
            # if mesh_dicts['hrr_dict'] != {}:
            #     hrr_lst.append(mesh_dicts['hrr_dict'])
            #     mesh_dicts['hrr_dict'] = {}
            #
            # if mesh_dicts['loss_dict'] != {}:
            #     loss_lst.append(mesh_dicts['loss_dict'])
            #     mesh_dicts['loss_dict'] = {}
            #
            # if mesh_dicts['lagrange_dict'] != {}:
            #     lagrange_lst.append(mesh_dicts['lagrange_dict'])
            #     mesh_dicts['lagrange_dict'] = {}
            #
            # if all(value != None for value in ts_dict.values()):
            #     ts_lst.append(ts_dict)
            #     ts_dict = dict.fromkeys(['time_step', 'sim_time', 'press_itr', 'm_error', 'log_time', 'cycles'])

            cycle_check = {}

        # Populate per cycle data
        cycle_fx_to_use = [key for key in per_cycle_dict.keys() if per_cycle_dict[key] is None]
        for fx in cycle_fx_to_use:
            scr.scrape(fx, line, per_cycle_dict, mesh_info = mesh_data['mesh_info'])

        current_mesh, mesh_line = scr.mesh_n(line, current_mesh, mesh_line)

        if current_mesh is not None:
            m_line_str = str(mesh_line)

            if m_line_str in scr.mesh_param_order.keys():
                for fx in scr.mesh_param_order[m_line_str]:

                    #TODO check dictionary names in scrapping functions
                    if fx in per_mesh_info['fx']:
                        success_line = scr.scrape_succs(fx, line, per_mesh_info['dict'], success_line,
                                                        n_mesh=current_mesh, mesh_info=mesh_data['mesh_info'])

                    if success_line:
                        break

            mesh_line = mesh_line + 1

        i = i + 1

#TODO - Write this as loops for each type of data

# Print last line
ts_lst.append(ts_dict)
ts_pd = pd.DataFrame(ts_lst)

cfl_lst.append(mesh_dicts['cfl_dict'])
cfl_pd = pd.DataFrame(cfl_lst)
cfl_pd['sim_time'] = ts_pd['sim_time']
cfl_pd['log_time'] = ts_pd['log_time']

max_div_lst.append(mesh_dicts['max_div_dict'])
max_div_pd = pd.DataFrame(max_div_lst)
max_div_pd['sim_time'] = ts_pd['sim_time']
max_div_pd['log_time'] = ts_pd['log_time']

min_div_lst.append(mesh_dicts['min_div_dict'])
min_div_pd = pd.DataFrame(min_div_lst)
min_div_pd['sim_time'] = ts_pd['sim_time']
min_div_pd['log_time'] = ts_pd['log_time']

hrr_lst.append(mesh_dicts['hrr_dict'])
hrr_pd = pd.DataFrame(hrr_lst)
hrr_pd['sim_time'] = ts_pd['sim_time']
hrr_pd['log_time'] = ts_pd['log_time']

loss_lst.append(mesh_dicts['loss_dict'])
loss_pd = pd.DataFrame(loss_lst)
loss_pd['sim_time'] = ts_pd['sim_time']
loss_pd['log_time'] = ts_pd['log_time']

vn_lst.append(mesh_dicts['vn_dict'])
vn_pd = pd.DataFrame(vn_lst)
vn_pd['sim_time'] = ts_pd['sim_time']
vn_pd['log_time'] = ts_pd['log_time']

cpu_step_lst.append(mesh_dicts['cpu_step_dict'])
cpu_step_pd = pd.DataFrame(cpu_step_lst)
cpu_step_pd['sim_time'] = ts_pd['sim_time']
cpu_step_pd['log_time'] = ts_pd['log_time']

cpu_tot_lst.append(mesh_dicts['cpu_tot_dict'])
cpu_tot_pd = pd.DataFrame(cpu_tot_lst)
cpu_tot_pd['sim_time'] = ts_pd['sim_time']
cpu_tot_pd['log_time'] = ts_pd['log_time']

lagrange_lst.append(mesh_dicts['lagrange_dict'])
lagrange_pd = pd.DataFrame(lagrange_lst)
lagrange_pd['sim_time'] = ts_pd['sim_time']
lagrange_pd['log_time'] = ts_pd['log_time']

print(i)

cfl_pd.to_csv(os.path.join(output_loc, 'cfl.csv'), index=False)
max_div_pd.to_csv(os.path.join(output_loc, 'max_div.csv'), index=False)
min_div_pd.to_csv(os.path.join(output_loc, 'min_div.csv'), index=False)
hrr_pd.to_csv(os.path.join(output_loc, 'hrr.csv'), index=False)
loss_pd.to_csv(os.path.join(output_loc, 'loss.csv'), index=False)
vn_pd.to_csv(os.path.join(output_loc, 'vn.csv'), index=False)
cpu_step_pd.to_csv(os.path.join(output_loc, 'cpu_step.csv'), index=False)
cpu_tot_pd.to_csv(os.path.join(output_loc, 'cpu_tot.csv'), index=False)
ts_pd.to_csv(os.path.join(output_loc, 'ts.csv'), index=False)
lagrange_pd.to_csv(os.path.join(output_loc, 'lagrange.csv'), index=False)
sim_info['date_start'] = sim_info['date_start'].strftime("%B %d, %Y %H:%M:%S")
with open(os.path.join(output_loc, 'data.json'), 'w') as fp:
    json.dump(sim_info, fp, indent=4)

print(time.time() - start_time)
print('asd')