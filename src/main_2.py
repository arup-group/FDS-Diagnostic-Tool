from builds import builds_control
from diag_summaries import diagnosticsSummary
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

# Load master config file
with open('config.json') as config_js:
    config = json.load(config_js)

# Process submit queue
submit_data = utils.prcs_submit_file(config)

sim_summaries = []

#TODO based on log define start entry

for entry in submit_data:
    errors_count = [0, 0, 0]
    try:
        sim = sim_info.diagnosticInfo(
            output_folder_name=entry,
            sim_name=submit_data[entry]['sim_name'],
            sim_input_fold=submit_data[entry]['input_folder'],
            config=config,
            is_cluster_running=submit_data[entry]['is_cluster_running'],
            cls_info=submit_data[entry]['cls_info'])

        sim_log = logging.getLogger('sim_log')
        sim.perform_checks()
        sim_log.info(f'*** START PROCESSING  {sim.sim_name} ***')
        main_log.info(f'Start processing  {sim.sim_name}.')
    except:
        errors_count[0] += 1
        try:
            sim.error_count = errors_count
            sim_log.critical(f'Error during initialisation for {entry}.', exc_info=True)
            sim.log.info(f'Finished processing  {sim.sim_name} with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
        except:
            main_log.exception(f'Error during initialisation for {entry}.')

        main_log.info(
            f'Finished processing  with {errors_count[0]} critical error, {errors_count[1]} errors, and {errors_count[2]} warnings.')
        continue

    # Save cls infor
    sim.save_cls_info()

    # Import correct module - critical
    try:
        mesh_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.mesh_tools')
        hrr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.hrr_tools')
        obstr_tools = importlib.import_module(f'{builds_control[sim.fds_ver]}.obstruction_tools')
        runtime_data = importlib.import_module(f'{builds_control[sim.fds_ver]}.runtime_data')
        plots_setup = importlib.import_module(f'{builds_control[sim.fds_ver]}.plots_setup')
    except KeyError:
        sim.error_count[0] += 1
        sim_log.critical(f'FDS version {sim.fds_ver} not supported.', exc_info=True)
        sim_log.info(
            f'Finished processing  with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
        main_log.info(
            f'Finished processing {sim.sim_name} with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
        continue

    # Process mesh data (warning - return none for mesh data)
    if sim.mesh_data is None:
        try:
            sim.mesh_data = mesh_tools.mesh_als(
                fds_path=sim.fds_f_loc,
                save_loc=sim.output_fold)
            sim_log.info('Mesh data processed.')
        except:
            sim.error_count[1] += 1
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
            sim.error_count[1] += 1
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
            sim.error_count[1] += 1
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
        sim.error_count[0] += 1
        sim_log.critical('Error processing runtime data.', exc_info=True)
        sim.log.info(
            f'Finished processing  with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
        main_log.info(
            f'Finished processing {sim.sim_name} with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
        continue

    # Process analytics (error - pass errors records)
    sim.run_analytics()

    #Plot (error and warnings when analytics info is not avaliable)
    sim_log.info('Plotting requested graphs.')
    plots_setup.plot(
            output_loc=sim.output_fold,
            plots_config=sim.config['plots'],
            analytics_res=sim.als_results,
            require_plots=sim.require_plots)

    # Copy source data (warning)
    if config['settings']['copy_source_f']:
        sim_log.info('Copying source files')
        try:
            sim.copy_source_files()
        except:
            sim.error_count[1] += 1
            sim_log.exception('Error copying source data.')

    # Report
    sim_summaries.append(sim.report_summary())

    sim_log.info(
        f'Finished processing  with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')
    main_log.info(
        f'Finished processing {sim.sim_name} with {sim.error_count[0]} critical error, {sim.error_count[1]} errors, and {sim.error_count[2]} warnings.')

main_log.info(f'Reporting summaries')
diag = diagnosticsSummary(
    input_entries=sim_summaries,
    save_loc=config["settings"]["output_loc"])
diag.process_summaries()
main_log.info(f'*** Diagnostics of all simulations completed. ***')

#TODO change sim_end to end_sim_time
#TODO copy src file and cluster file if relevant

print('END OF PROGRAM')