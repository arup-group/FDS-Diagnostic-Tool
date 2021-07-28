# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:54:01 2019

@author: javor
"""

import scraping_fxn as scr
import analysis_fxn as anf
import pandas as pd
import time
import json
import os

start_time = time.time()

doc_file_path = r"C:\work\fds_diagnostics\docs\paisley\Fire_Scenario_4_VentOption1.out"
fds_file = r"C:\work\fds_diagnostics\docs\paisley\Fire_Scenario_4_VentOption1.fds"
output_loc = r'C:\work\fds_diagnostics\src\outputs\paisley'

# Mesh setup
cycle_check = {}

# Mesh setup
data_dict = dict.fromkeys(['ver', 'date_start', 'sim_end', 'cores_n', 'tot_elp_time'])
data_dict = scr.mesh_info(fds_file, data_dict)
data_dict = anf.tot_el(data_dict)
data_dict = anf.grid_size(data_dict)
data_dict = anf.tot_volume(data_dict)
data_dict = anf.model_range(data_dict)

# ts_dict setup
ts_dict = dict.fromkeys(['time_step', 'compl_time', 'press_itr', 'm_error', 'log_time', 'cycles'])
ts_lst = list()

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

        # Populate data dict
        fx_to_use = [key for key in data_dict.keys() if data_dict[key] is None]
        for fx in fx_to_use:
            scr.scrape(fx, line, data_dict)

        # Populate mesh dicts
        scr.scrape('itr_date', line, cycle_check)

        if 'cycles' in cycle_check:

            if mesh_dicts['cfl_dict'] != {}:
                cfl_lst.append(mesh_dicts['cfl_dict'])
                mesh_dicts['cfl_dict'] = {}

            if mesh_dicts['cpu_step_dict'] != {}:
                cpu_step_lst.append(mesh_dicts['cpu_step_dict'])
                mesh_dicts['cpu_step_dict'] = {}

            if mesh_dicts['cpu_tot_dict'] != {}:
                cpu_tot_lst.append(mesh_dicts['cpu_tot_dict'])
                mesh_dicts['cpu_tot_dict'] = {}

            if mesh_dicts['vn_dict'] != {}:
                vn_lst.append(mesh_dicts['vn_dict'])
                mesh_dicts['vn_dict'] = {}

            if mesh_dicts['max_div_dict'] != {}:
                max_div_lst.append(mesh_dicts['max_div_dict'])
                mesh_dicts['max_div_dict'] = {}

            if mesh_dicts['min_div_dict'] != {}:
                min_div_lst.append(mesh_dicts['min_div_dict'])
                mesh_dicts['min_div_dict'] = {}

            if mesh_dicts['hrr_dict'] != {}:
                hrr_lst.append(mesh_dicts['hrr_dict'])
                mesh_dicts['hrr_dict'] = {}

            if mesh_dicts['loss_dict'] != {}:
                loss_lst.append(mesh_dicts['loss_dict'])
                mesh_dicts['loss_dict'] = {}

            if mesh_dicts['lagrange_dict'] != {}:
                lagrange_lst.append(mesh_dicts['lagrange_dict'])
                mesh_dicts['lagrange_dict'] = {}

            if all(value != None for value in ts_dict.values()):
                ts_lst.append(ts_dict)
                ts_dict = dict.fromkeys(['time_step', 'compl_time', 'press_itr', 'm_error', 'log_time', 'cycles'])

            cycle_check = {}

        # Populate ts_dict
        fx_to_use2 = [key for key in ts_dict.keys() if ts_dict[key] is None]
        for fx in fx_to_use2:  # BREAK OUT
            scr.scrape(fx, line, ts_dict, mesh_info=data_dict['mesh_info'])

        current_mesh, mesh_line = scr.mesh_n(line, current_mesh, mesh_line)

        if current_mesh is not None:
            m_line_str = str(mesh_line)

            if m_line_str in scr.mesh_param_order.keys():
                for fx in scr.mesh_param_order[m_line_str]:
                    success_line = scr.scrape_succs(fx, line, mesh_dicts, success_line, n_mesh=current_mesh,
                                                    mesh_info=data_dict['mesh_info'])

                    if success_line == True:
                        break

            mesh_line = mesh_line + 1

        i = i + 1

# Print last line
ts_lst.append(ts_dict)
ts_pd = pd.DataFrame(ts_lst)

cfl_lst.append(mesh_dicts['cfl_dict'])
cfl_pd = pd.DataFrame(cfl_lst)
cfl_pd['compl_time'] = ts_pd['compl_time']
cfl_pd['log_time'] = ts_pd['log_time']

max_div_lst.append(mesh_dicts['max_div_dict'])
max_div_pd = pd.DataFrame(max_div_lst)
max_div_pd['compl_time'] = ts_pd['compl_time']
max_div_pd['log_time'] = ts_pd['log_time']

min_div_lst.append(mesh_dicts['min_div_dict'])
min_div_pd = pd.DataFrame(min_div_lst)
min_div_pd['compl_time'] = ts_pd['compl_time']
min_div_pd['log_time'] = ts_pd['log_time']

hrr_lst.append(mesh_dicts['hrr_dict'])
hrr_pd = pd.DataFrame(hrr_lst)
hrr_pd['compl_time'] = ts_pd['compl_time']
hrr_pd['log_time'] = ts_pd['log_time']

loss_lst.append(mesh_dicts['loss_dict'])
loss_pd = pd.DataFrame(loss_lst)
loss_pd['compl_time'] = ts_pd['compl_time']
loss_pd['log_time'] = ts_pd['log_time']

vn_lst.append(mesh_dicts['vn_dict'])
vn_pd = pd.DataFrame(vn_lst)
vn_pd['compl_time'] = ts_pd['compl_time']
vn_pd['log_time'] = ts_pd['log_time']

cpu_step_lst.append(mesh_dicts['cpu_step_dict'])
cpu_step_pd = pd.DataFrame(cpu_step_lst)
cpu_step_pd['compl_time'] = ts_pd['compl_time']
cpu_step_pd['log_time'] = ts_pd['log_time']

cpu_tot_lst.append(mesh_dicts['cpu_tot_dict'])
cpu_tot_pd = pd.DataFrame(cpu_tot_lst)
cpu_tot_pd['compl_time'] = ts_pd['compl_time']
cpu_tot_pd['log_time'] = ts_pd['log_time']

lagrange_lst.append(mesh_dicts['lagrange_dict'])
lagrange_pd = pd.DataFrame(lagrange_lst)
lagrange_pd['compl_time'] = ts_pd['compl_time']
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
data_dict['date_start'] = data_dict['date_start'].strftime("%B %d, %Y %H:%M:%S")
with open(os.path.join(output_loc, 'data.json'), 'w') as fp:
    json.dump(data_dict, fp, indent=4)

print(time.time() - start_time)
