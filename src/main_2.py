from builds import builds_control
import analytical_models.process_models as amp
import sim_info
import utils
import json
import os
from shutil import copyfile
import importlib



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
        sim.perform_checks()
    except:
        sim.logger.critical(f'Error during initialisation for {entry}.', exc_info=True)

print('here')
