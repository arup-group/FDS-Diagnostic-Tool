from builds import builds_control
import analytical_models.process_models as amp
import sim_info
import utils
import json
import os
from shutil import copyfile
import importlib
import logging


#TODO SETUP MASTER LOG
main_log = utils.setup_logger('main_log', 'logs/main_log.log')
main_log.info('*** FDS DIAGNOSTICS v0.2.0 Beta STARTED ***')

# Process submit queue
submit_data = utils.prcs_submit_file('submit_sim.txt')

# Load master config file
with open('config.json') as config_js:
    config = json.load(config_js)

for entry in submit_data:
    errors_count = [0, 0, 0]
    try:
        sim = sim_info.diagnosticInfo(
            sim_name=entry,
            sim_input_fold=submit_data[entry],
            config=config,
            is_cluster_running=True)
        sim_log = logging.getLogger('sim_log') #Get sim log
        sim.perform_checks()
        sim_log.info(f'*** START PROCESSING  {sim.sim_name} ***')
        main_log.info(f'Start processing  {sim.sim_name}.')
    except:
        errors_count[0] += 1
        try:
            sim_log.critical(f'Error during initialisation for {entry}.', exc_info=True)
            sim.log.info(f'Finished processing  {sim.sim_name} with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')

        except:
            main_log.exception(f'Error during initialisation for {entry}.')

        main_log.info(
            f'Finished processing  with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        continue

    # Import correct module - critical
    try:
        mesh_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.mesh_tools')
        hrr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.hrr_tools')
        obstr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.obstruction_tools')
        runtime_data = importlib.import_module(f'{builds_control[sim.fds_ver]}.runtime_data')
        plots_setup = importlib.import_module(f'{builds_control[sim.fds_ver]}.plots_setup')
    except KeyError:
        errors_count[0] += 1
        sim_log.critical(f'FDS version {sim.fds_ver} not supported.', exc_info=True)
        sim_log.info(
            f'Finished processing  with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        main_log.info(
            f'Finished processing {sim.sim_name} with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        continue

    # Process mesh data (warning - return none for mesh data)
    if sim.mesh_data is None:
        try:
            sim.mesh_data = mesh_tools.mesh_als(
                fds_path=sim.fds_f_loc,
                save_loc=sim.output_fold)
            sim_log.info('Mesh data processed.')
        except:
            sim.errors_count[1] += 1
            sim_log.exception('Error loading mesh data.')
            mesh_data = None


    # Process HRR data (warning)
    if sim.require_hrr_data:
        try:
            hrr_tools.get_hrr_data(
                fds_f_path=sim.fds_f_loc,
                save_loc=sim.output_fold,
                hrr_curve_sampling_rate=1)
            sim.require_hrr_data = False
            sim_log.info('HRR data processed.')
        except:
            sim.errors_count[1] += 1
            sim_log.exception('Error processing hrr data.')


    # Process image data (warning)
    if sim.require_img_data:
        try:
            obstr_tools.process_obstructions(
                output_path=sim.output_fold,
                fds_filepath=sim.fds_f_loc)
            sim.require_img_data = False
            sim_log.info('Image data processed.')
        except:
            sim.errors_count[1] += 1
            sim_log.exception('Error processing obstruction.')


    # Process runtime data (critical)
    try:
        sim_log.info(f'Start runtime data parsing using build {builds_control[sim.fds_ver]}.')
        runtime_data.get_data(
            outfile_file_path=sim.out_f_loc,
            output_loc=sim.output_fold,
            config=sim.config,
            mesh_data=sim.mesh_data)
    except:
        sim.errors_count[0] += 1
        sim_log.critical('Error processing runtime data.', exc_info=True)
        sim.log.info(
            f'Finished processing  with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        main_log.info(
            f'Finished processing {sim.sim_name} with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        continue

    # Process analytics (error - pass errors records)
    sim.run_analytics(errors_count)

    #Plot (error and warnings when analytics info is not avaliable)
    sim_log.info('Plotting requested graphs.')
    plots_setup.plot(
            output_loc=sim.output_fold,
            plots_config=sim.config['plots'],
            analytics_res=sim.als_results,
            require_plots=sim.require_plots)


    sim_log.info(
        f'Finished processing  with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
    main_log.info(
        f'Finished processing {sim.sim_name} with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')

main_log.info(f'*** Diagnostics of all simulations completed. ***')

#TODO change sim_end to end_sim_time

print('END OF PROGRAM')