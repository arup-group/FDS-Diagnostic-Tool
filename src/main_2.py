from builds import builds_control
import analytical_models.process_models as amp
import sim_info
import utils
import json
import os
from shutil import copyfile
import importlib
import logging



#main_log = utils.setup_logger('main_log', 'logs/main_log.log')
#main_log.info('*** FDS DIAGNOSTICS v0.1.0 Beta STARTED ***')

# Process submit queue
submit_data = utils.prcs_submit_file('submit_sim.txt')

# Load master config file
with open('config.json') as config_js:
    config = json.load(config_js)

for entry in submit_data:
    try:
        sim = sim_info.diagnosticInfo(
            sim_name=entry,
            sim_input_fold=submit_data[entry],
            config=config)
        sim_log = logging.getLogger('sim_log') #Get sim log
        sim.perform_checks()
    except:
        sim_log.critical(f'Error during initialisation for {entry}.', exc_info=True)

    # Import correct module - critical
    try:
        mesh_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.mesh_tools')
        hrr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.hrr_tools')
        obstr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.obstruction_tools')
        runtime_data = importlib.import_module(f'{builds_control[sim.fds_ver]}.runtime_data')
        plots_setup = importlib.import_module(f'{builds_control[sim.fds_ver]}.plots_setup')
    except KeyError:
        sim_log.critical(f'FDS version {sim.fds_ver} not supported.', exc_info=True)

    # Process mesh data
    if sim.mesh_data is None:
        sim.mesh_data = mesh_tools.mesh_als(
            fds_path=sim.fds_f_loc,
            save_loc=sim.output_fold)
        sim_log.info('Mesh data processed.')

    # Process HRR data
    if sim.require_hrr_data:
        hrr_tools.get_hrr_data(
            fds_f_path=sim.fds_f_loc,
            save_loc=sim.output_fold,
            hrr_curve_sampling_rate=1)
        sim.require_hrr_data = False
        sim_log.info('HRR data processed.')

    # Process image data
    if sim.require_img_data:
        obstr_tools.process_obstructions(
            output_path=sim.output_fold,
            fds_filepath=sim.fds_f_loc)
        sim.require_img_data = False
        sim_log.info('Image data processed.')



    # Process runtime data




#print('here')