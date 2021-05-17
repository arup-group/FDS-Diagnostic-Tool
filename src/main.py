from builds import builds_control
import analytical_models.process_models as amp
import utils
import json
import os
from shutil import copyfile
import importlib

#Results for testing only TODO - to be reomved later
results = {}

# Process submit queue
submit_data = utils.prcs_submit_file('submit_sim.txt')

# Load master config file
with open('config.json') as config_js:
    config = json.load(config_js)

# Start looping for each part of the queue
for sim in submit_data:
    print(f'*** START PROCESSING {sim} ***')

    sim_output_loc = os.path.join(config['settings']['output_loc'], sim)

    # Create diagnostic output folder structure (works once)
    utils.create_diag_dirs(sim_output_loc)

    # Get relevant locations for each simulation
    inpt_f_loc = utils.get_inpt_files_loc(submit_data[sim])

    # Copy configuration settings (only first time) and reload it
    config_sim_path = os.path.join(sim_output_loc, 'config.json')
    if os.path.isfile(config_sim_path):
        with open(config_sim_path) as config_js:
            config = json.load(config_js)
        print('Sim config loaded.')
    else:
        copyfile('config.json', config_sim_path)
        with open(config_sim_path) as config_js:
            config = json.load(config_js)
        print('Sim config copied and loaded.')

    # Get version
    ver = utils.get_version(inpt_f_loc['out_f_loc'])

    # Import correct module
    mesh_tools = importlib.import_module(f'{builds_control[ver]}.mesh_tools')
    hrr_tools = importlib.import_module(f'{builds_control[ver]}.hrr_tools')
    obstr_tools = importlib.import_module(f'{builds_control[ver]}.obstruction_tools')
    runtime_data = importlib.import_module(f'{builds_control[ver]}.runtime_data')
    plots_setup = importlib.import_module(f'{builds_control[ver]}.plots_setup')

    # START PROCESSING SERVICES

    # Get mesh info (only first time)
    if os.path.isfile(os.path.join(sim_output_loc, 'data', 'mesh_data.json')):
        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json')) as f:
            mesh_data = json.load(f)
        print('Mesh data loaded.')
    else:
        mesh_data = mesh_tools.mesh_als(inpt_f_loc['fds_f_loc'])
        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json'), 'w') as f:
            json.dump(mesh_data, f, indent=4)
        print('Mesh data processed.')


    # Get fire curve info (only first time)
    if os.path.isfile(os.path.join(sim_output_loc, 'data', 'hrr_data.json')):
        print('HRR data available.')
    else:
        hrr_tools.get_hrr_data(inpt_f_loc['fds_f_loc'], sim_output_loc, hrr_curve_sampling_rate=1)
        print('HRR data processed.')


    # Create images (only first time)
    if os.path.isfile(os.path.join(sim_output_loc, 'imgs', 'xy.png')):
        print('Obstruction data available.')
    else:
        obstr_tools.process_obstrctions(sim_output_loc, inpt_f_loc['fds_f_loc'])


    # Get runtime data
    print(f'Start runtime data parsing using {builds_control[ver]}.')
    runtime_data.get_data(inpt_f_loc['out_f_loc'], sim_output_loc, config, mesh_data)


    #Run analytics
    als_res = amp.run_analytics(sim_output_loc)
    print('Analytical models processed.')


    # Plot results
    print('Start plotting.')
    plots_setup.plot(sim_output_loc, config['plots'], als_res)
    print('Finish plotting.')
    print(f'*** FINISHED PROCESSING {sim} ***')
    # Call default plotting function
print('*** SCRIPT TERMINATED ***')