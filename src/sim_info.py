import analytical_models as am
import json
import os
import glob
import re
import logging
import sys
from shutil import copyfile
import datetime
import random


class diagnosticInfo:

    def __init__(self, sim_name, sim_input_fold, config, is_cluster_running, cls_info):

        self.sim_name = sim_name
        self.sim_input_fold = sim_input_fold
        self.config = config
        self.is_cluster_running = is_cluster_running
        self.cls_info = cls_info
        self.out_f_loc = None
        self.fds_f_loc = None
        self.output_fold = None
        self.fds_ver = None
        self.current_time = datetime.datetime.now()

        # Parameters always needed for adequate functioning
        self.mesh_data = None
        self.error_count = [0, 0, 0]

        # Configurable parameters
        self.require_hrr_data = None
        self.require_img_data = None
        self.require_plots = {'mesh': None, 'cycle': None, 'loc': None, 'time_progress': None}

        self.als_results = {}

        self._get_output_fold_loc()
        self._create_folder_structure()
        self._setup_logger()


    def perform_checks(self):
        self._get_inpt_files_loc()
        self._setup_config_files()
        self._get_fds_version()
        self._check_mesh_data()
        self._check_hrr_data()
        self._check_img_data()
        self._check_plots_data()

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

    def _check_plots_data(self):
        """Checks which plots to perform"""

        if any([self.config['plots'][k] for k in ['min_div', 'max_div', 'vn', 'cfl', 'ts', 'ts_time']]):
            self.require_plots['mesh'] = True
        else:
            self.require_plots['mesh'] = False
        if any([self.config['plots'][k] for k in ['vel_err', 'press_err', 'press_itr', 'hrr']]):
            self.require_plots['cycle'] = True
        else:
            self.require_plots['cycle'] = False
        if any([self.config['plots'][k] for k in ['vn_loc', 'max_div_loc', 'min_div_loc', 'cfl_loc', 'vel_err_loc', 'press_err_loc']]):
            self.require_plots['loc'] = True
        else:
            self.require_plots['loc'] = False
        if self.config['plots']['time_progress']:
            self.require_plots['time_progress'] = True
        else:
            self.require_plots['time_progress'] = False

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
        sim_log = logging.getLogger('sim_log')

        #Run status prediction analytics
        try:
            stats_pred = am.status_prediction.predictSimStatus(
                output_loc=self.output_fold,
                cur_time=self.current_time,
                is_cluster_running=self.is_cluster_running)
            self.als_results['sim_status'] = stats_pred.report_status()
        except:
            self.error_count[1] += 1
            sim_log.exception('Error in status prediction analytics.')
            self.als_results['sim_status'] = None
        #run rtp analytics
        try:
            rtp_model = am.rtp.mAvg(
                output_loc=self.output_fold,
                mavg_window=30,
                n_predictions=7,
                sim_status=self.als_results['sim_status']['status'])
            rtp_model.run_model()
            self.als_results['rtp'] = rtp_model.report_results()
            self.dummy_class = rtp_model
        except:
            self.error_count[1] += 1
            sim_log.exception('Error in runtime prediction analytics.')
            self.als_results['rtp'] = None

        with open(os.path.join(self.output_fold, 'data', 'als_results.json'), 'w') as fp:
            json.dump(self.als_results, fp, indent=4)

        sim_log.info('Analytical models processed.')

    def _save_cls_info(self):
        with open(os.path.join(self.output_fold, 'data', 'cls_info.json'), 'w') as fp:
            json.dump(self.cls_info, fp, indent=4)


    def report_summary(self):
        """Reports summary for overview visualisations"""
        sim_report = {}
        sim_report['sim_status'] = self.als_results['sim_status']
        sim_report['rtp'] = self.als_results['rtp']
        sim_report['sim_name'] = self.sim_name
        sim_report['cls_ID'] = self.cls_info['cls_ID']
        sim_report['user_ID'] = self.cls_info['user_ID']
        sim_report['diagnostic_error_count'] = self.error_count

        #Save machine infoemation
        self._save_cls_info()

        return sim_report

