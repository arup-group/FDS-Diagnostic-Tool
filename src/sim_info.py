import analytical_models as am
import json
import os
import glob
import re
import logging
import sys
from shutil import copyfile
import datetime



class diagnosticInfo:

    def __init__(self, sim_name, sim_input_fold, config):

        self.sim_name = sim_name
        self.sim_input_fold = sim_input_fold
        self.config = config
        self.out_f_loc = None
        self.fds_f_loc = None
        self.output_fold = None
        self.fds_ver = None
        self.current_time = datetime.datetime.now()

        # Parameters always needed for adequate functioning
        self.mesh_data = None

        # Configurable parameters
        self.require_hrr_data = None
        self.require_img_data = None

        self.n_warn = 0
        self.n_crit = 0
        self.n_err = 0
        self.als_results = {}

        self._get_output_fold_loc()
        self._get_inpt_files_loc()
        self._create_folder_structure()
        self._setup_logger()
        self.logger.info(f'*** START PROCESSING  {self.sim_name} ***')

    def perform_checks(self):
        self._setup_config_files()
        self._get_fds_version()
        self._check_mesh_data()
        self._check_hrr_data()
        self._check_img_data()

    def _get_inpt_files_loc(self):
        '''Gets the location of the fds and out files'''

        fds_files = glob.glob(os.path.join(self.sim_input_fold, '*.fds'))
        if len(fds_files) == 1:
            self.fds_f_loc = fds_files[0]
        else:
            raise Exception('Multiple or no *.fds files')

        out_files = glob.glob(os.path.join(self.sim_input_fold, '*.out'))
        if len(out_files) == 1:
            self.out_f_loc = out_files[0]
        else:
            raise Exception('Multiple or no *.out files')

    def _get_output_fold_loc(self):
        '''Gets output folder for simulation run'''
        self.output_fold = os.path.join(self.config['settings']['output_loc'], self.sim_name)

    def _create_folder_structure(self):
        """"Creates appropriate subfolders"""

        subfolders = ['logs', 'data', 'imgs', 'inf']
        for subf in subfolders:
            os.makedirs(os.path.join(self.output_fold, subf), exist_ok=True)

    def _setup_config_files(self):
        """Checks if there is a config file in output folder location. If yes loads that one
        and replaces current config. If no copies master config and loads it"""

        config_sim_path = os.path.join(self.output_fold, 'config.json')
        if os.path.isfile(config_sim_path):
            with open(config_sim_path) as config_js:
                self.config = json.load(config_js)
                self.logger.info('Diagnostic configuration loaded.')
        else:
            copyfile('config.json', config_sim_path)
            with open(config_sim_path) as config_js:
                self.config = json.load(config_js)
                self.logger.info('Diagnostic configuration copied and loaded.')

    def _check_mesh_data(self):

        """Checks if mesh data is present and load it"""

        if os.path.isfile(os.path.join(self.output_fold, 'data', 'mesh_data.json')):
            with open(os.path.join(self.output_fold, 'data', 'mesh_data.json')) as f:
                self.mesh_data = json.load(f)
                self.logger.info('Mesh data loaded.')
        else:
            self.mesh_data = None

    def _check_img_data(self):
        """Checks if image data data is present."""

        if os.path.isfile(os.path.join(self.output_fold, 'imgs', 'xy.png')):
            self.require_img_data = False
            self.logger.info('Image data available.')
        elif self.config['utils']['obstruction_als']:
            self.require_img_data = True
        else:
            self.require_img_data = False

    def _check_hrr_data(self):
        """Checks if image data data is present."""

        if os.path.isfile(os.path.join(self.output_fold, 'data', 'hrr_data.json')):
            self.require_hrr_data = False
            self.logger.info('HRR data available.')
        elif self.config['utils']['hrr_als']:
            self.require_hrr_data = True
        else:
            self.require_hrr_data = False

    def _get_fds_version(self):
        ver_ptn = r'(?:[Vv]ersion|[Rr]evision)[\s:A-Za-z]+(\d+\.\d+\.\d+)'

        with open(self.out_f_loc, "r", errors='ignore') as file:
            for line in file:
                search_result = re.search(ver_ptn, line)
                if search_result is not None:
                    self.fds_ver = search_result.group(1)
                    self.logger.info(f'Simulation FDS version identified as {self.fds_ver}.')
                    break
            if self.fds_ver is None:
                raise Exception('Supported FDS version is not detected.')

    def _setup_logger(self, level=logging.INFO):

        format = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        self.logger = logging.getLogger('sim_log')
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        file_handler = logging.FileHandler(os.path.join(self.output_fold, 'logs', 'sim_log.log'), mode='a')
        file_handler.setFormatter(format)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(format)

        self.logger.setLevel(level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.propagate = False

    def run_analytics(self):
        """Starts relevant analytics based on configuration"""

        #Run status prediction analytics
        stats_pred = am.status_prediction.predictSimStatus(
            output_loc=self.output_fold,
            cur_time=self.current_time)
        self.dummy_class = stats_pred
        self.als_results['sim_status'] = stats_pred.report_status()


    def report_summary(self):
        """Reports summary for overview visualisations"""
        pass