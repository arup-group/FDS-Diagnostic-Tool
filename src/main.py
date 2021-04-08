import utils
import json
import os
from shutil import copyfile


# Process submit queue
submit_data = utils.prcs_submit_file('submit_sim.txt')

# Load master config file
with open('config.json') as config_js:
    config = json.load(config_js)

# Start looping for each part of the queue
for sim in submit_data:

    sim_output_loc = os.path.join(config['settings']['output_loc'], sim)
    print(sim_output_loc)

    # Create diagnostic output folder structure (works once)
    utils.create_diag_dirs(sim_output_loc)

    # Get relevant locations for each simulation

    inpt_f_loc = utils.get_inpt_files_loc(submit_data[sim])

    # Copy configuration settings (only first time) and reload it
    config_sim_path = os.path.join(sim_output_loc, 'config.json')
    if os.path.isfile(config_sim_path):
        with open(config_sim_path) as config_js:
            config = json.load(config_js)
        print('sim config loaded')

    else:
        copyfile('config.json', config_sim_path)
        with open(config_sim_path) as config_js:
            config = json.load(config_js)
        print('sim config copied and loaded')

    # Get version (only first time)
    ver = utils.get_version(inpt_f_loc['out_f_loc'])

    # Import correct module
    if ver == 'FDS 6.1.2':
        from b612 import mesh_tools, runtime_data

    # START PROCESSING SERVICES

    # Get mesh info (only first time)
    if os.path.isfile(os.path.join(sim_output_loc, 'data', 'mesh_data.json')) == False :
        mesh_data = mesh_tools.mesh_als(inpt_f_loc['fds_f_loc'])
        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json'), 'w') as f:
            json.dump(mesh_data, f, indent=4)
    else:
        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json')) as f:
            mesh_data = json.load(f)

    # Get fire curve info (only first time)

    # Create images (only forst time)

    # Get runtime data
    runtime_data.get_data(inpt_f_loc['out_f_loc'], sim_output_loc, config, mesh_data)

    # Plot results
