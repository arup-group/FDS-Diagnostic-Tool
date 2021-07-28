from builds import builds_control
import analytical_models.process_models as amp
import utils
import json
import os
from shutil import copyfile
import importlib

def main():

    #Setup log
    main_log = utils.setup_logger('main_log', 'logs/main_log.log')
    main_log.info('*** FDS DIAGNOSTICS v0.1.0 Beta STARTED ***')

    try:

        # Process submit queue
        submit_data = utils.prcs_submit_file('submit_sim.txt')

        # Load master config file
        with open('config.json') as config_js:
            config = json.load(config_js)

        # Start looping for each part of the queue - critical
        for sim in submit_data:
            n_err = 0
            n_crit = 0
            n_warn = 0

            try:
                main_log.info(f'Start processing  {sim}.')

                sim_output_loc = os.path.join(config['settings']['output_loc'], sim)

                # Create diagnostic output folder structure (works once)
                utils.create_diag_dirs(sim_output_loc)

                #Setup log
                sim_log = utils.setup_logger('sim_log', os.path.join(sim_output_loc, 'logs', 'sim_log.log'))
                sim_log.info(f'*** START PROCESSING  {sim} ***')


                # Get relevant locations for each simulation - critical
                inpt_f_loc = utils.get_inpt_files_loc(submit_data[sim])

                # Copy configuration settings (only first time) and reload it
                config_sim_path = os.path.join(sim_output_loc, 'config.json')
                if os.path.isfile(config_sim_path):
                    with open(config_sim_path) as config_js:
                        config = json.load(config_js)
                    sim_log.info('Sim config loaded.')

                else:
                    copyfile('config.json', config_sim_path)
                    with open(config_sim_path) as config_js:
                        config = json.load(config_js)
                    sim_log.info('Sim config copied and loaded.')

                # Get version
                ver = utils.get_version(inpt_f_loc['out_f_loc'])

                # Import correct module - critical
                mesh_tools = importlib.import_module(f'{builds_control[ver]}.mesh_tools')
                hrr_tools = importlib.import_module(f'{builds_control[ver]}.hrr_tools')
                obstr_tools = importlib.import_module(f'{builds_control[ver]}.obstruction_tools')
                runtime_data = importlib.import_module(f'{builds_control[ver]}.runtime_data')
                plots_setup = importlib.import_module(f'{builds_control[ver]}.plots_setup')

                # START PROCESSING SERVICES

                # Get mesh info (only first time) - warning
                try:
                    if os.path.isfile(os.path.join(sim_output_loc, 'data', 'mesh_data.json')):
                        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json')) as f:
                            mesh_data = json.load(f)
                        sim_log.info('Mesh data loaded.')
                    else:
                        mesh_data = mesh_tools.mesh_als(inpt_f_loc['fds_f_loc'])
                        with open(os.path.join(sim_output_loc, 'data', 'mesh_data.json'), 'w') as f:
                            json.dump(mesh_data, f, indent=4)
                        sim_log.info('Mesh data processed.')
                except:
                    mesh_data = None
                    n_warn += 1
                    sim_log.exception("Error loading mesh data.")


                # Get fire curve info (only first time) - warning
                if config['utils']['hrr_als']:
                    try:
                        if os.path.isfile(os.path.join(sim_output_loc, 'data', 'hrr_data.json')):
                            sim_log.info('HRR data available.')
                        else:
                            hrr_tools.get_hrr_data(inpt_f_loc['fds_f_loc'], sim_output_loc, hrr_curve_sampling_rate=1)
                            sim_log.info('HRR data processed.')
                    except:
                        n_warn += 1
                        sim_log.exception("Error acquiring HRR data.")


                # Create images (only first time) - warning
                if config['utils']['obstruction_als']:
                    try:
                        if os.path.isfile(os.path.join(sim_output_loc, 'imgs', 'xy.png')):
                            sim_log.info('Obstruction data available.')
                        else:
                            obstr_tools.process_obstructions(sim_output_loc, inpt_f_loc['fds_f_loc'])
                    except:
                        n_warn += 1
                        sim_log.exception("Error acquiring img data.")


                # Get runtime data - critical
                sim_log.info(f'Start runtime data parsing using {builds_control[ver]}.')
                runtime_data.get_data(inpt_f_loc['out_f_loc'], sim_output_loc, config, mesh_data)

                #Run analytics - error
                als_res = amp.run_analytics(sim_output_loc)
                sim_log.info('Analytical models processed.')


                # Plot results
                sim_log.info('Plotting requested graphs.')
                plots_setup.plot(sim_output_loc, config['plots'], als_res)

                # Log results
                sim_log.info(f'*** FINISHED PROCESSING {sim} ***')

            except:
                n_err += 1
                sim_log.critical(f'Error in {sim}.', exc_info=True)

            finally:
                main_log.info(f'Finished processing  {sim} witn {n_warn} warnings, {n_err} errors, and {n_crit} critical errors.')

        main_log.info('*** FDS DIAGNOSTICS CONCLUDED ***')

    except:
        main_log.critical(f'Error in main script.', exc_info=True)


if __name__ == "__main__":
    main()
