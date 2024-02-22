import pandas as pd
import json
import os
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt

def round_to_hour_min(time_interv):
    '''Rounds confidence interval to h:min format'''
    time_interv_sec = abs(time_interv*3600)
    hours, remainder = divmod(time_interv_sec, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f'{hours:.0f}:{int(minutes):02d}'

class mAvg:
    def __init__(self, output_loc, mavg_window, n_predictions, sim_status):
        self.mavg_window = mavg_window
        self.n_predictions = n_predictions
        self.output_loc = output_loc
        self.sim_status = sim_status
        self.model_name = f'mAvg-{mavg_window}-v0.1.0'

        self.sim_time_start = None
        self.sim_time_end = None
        self.data = None
        self.times_to_predict = None
        self.predictions = None
        self.conf_intervals = None
        self.avg_spd = None
        self.avg_spd_ci = None

        self._load_data()
        self._determine_status()

    def _load_data(self):
        """Loads appropriate data for the model"""

        self.data = pd.read_csv(os.path.join(self.output_loc, 'data', 'cycle_info.csv'),
                                usecols=['log_time', 'sim_time'],
                                parse_dates=['log_time'])

        with open(os.path.join(self.output_loc, 'data', 'sim_info.json')) as f:
            sim_info = json.load(f)
        self.sim_time_end = sim_info['sim_end']
        self.sim_date_start = sim_info['date_start']

    def _determine_status(self):

        if self.sim_status in ['running', 'delayed']:
            if len(self.data.index) > self.mavg_window:
                self.model_status = 'to_run'
            else:
                self.model_status = 'no_data'
        else:
            self.model_status = 'no_run'


    def _get_times_to_predict(self):
        """The method calculates which times to predict"""

        time_range = np.linspace(0, self.sim_time_end, self.n_predictions)[1:]
        self.times_to_predict = time_range[time_range > self.data['sim_time'].iloc[-1]].astype(int)

    def _calc_spd(self):
        """Calculates simmulation sppeeds"""

        self.data['time_diff'] = self.data['log_time'].diff().dt.total_seconds()
        self.data['sim_time_diff'] = self.data['sim_time'].diff()
        self.data['sim_speed'] = self.data['sim_time_diff'] / self.data['time_diff'] * 3600  # sims/h

        if self.model_status == 'no_data':
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[0]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[0]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()

        elif self.model_status == 'to_run':
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[-self.mavg_window]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[-self.mavg_window]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()

    def _estimate_predicted_times(self):

        t_deltas = (self.times_to_predict - self.data['sim_time'].iloc[-1]) / self.avg_spd
        self.predictions = [self.data['log_time'].iloc[-1] + timedelta(hours=k) for k in t_deltas]
        self.conf_intervals = t_deltas - (self.times_to_predict - self.data['sim_time'].iloc[-1]) / (self.avg_spd - self.avg_spd_ci)

    def run_model(self):
        if self.model_status in ['to_run', 'no_data']:
            self._calc_spd()
            self._get_times_to_predict()
            self._estimate_predicted_times()

    def report_results(self):

        results = {}
        results['model_name'] = self.model_name
        results['model_status'] = self.model_status
        results['mavg_window'] = float(self.mavg_window)
        results['sim_pred_end'] = []
        results['sim_pred_end_unc'] = []
        results['predicts'] = []
        results['avg_spd'] = []
        results['avg_spd_ci'] = []


        if self.model_status in ['to_run', 'no_data']:

            for time_pr, value_pr, interv_pr, in zip(self.times_to_predict, self.predictions, self.conf_intervals):
                res = {}
                res['t'] = float(time_pr)
                res['pr_date'] = value_pr.strftime("%d/%m/%Y %H:%M:%S")
                res['unc'] = round_to_hour_min(interv_pr)
                if time_pr < self.sim_time_end:
                    res['pr_type'] = 'mid'
                else:
                    res['pr_type'] = 'end'
                    results['sim_pred_end'] = value_pr.strftime("%d/%m/%Y %H:%M:%S")
                    results['sim_pred_end_unc'] = round_to_hour_min(interv_pr)
                results['predicts'].append(res)

            results['avg_spd'] = round(self.avg_spd, 1)
            results['avg_spd_ci'] = round(self.avg_spd_ci, 1)

        return results


    def log(self, log_to_file = True, use_file = None):

        log_filename = f'{self.model_name}_log.json'
        log_res = {}
        log_res['sim_time'] = self.data['sim_time'].iloc[-1]

        for time_pr, value_pr, interv_pr, in zip(self.times_to_predict, self.predictions, self.conf_intervals):
            log_res[f'T{time_pr:.0f}'] = (value_pr - self.data['log_time'].iloc[0]).total_seconds()/3600
            log_res[f'T{time_pr:.0f}_unc'] = interv_pr

        if log_to_file:
            if os.path.isfile(os.path.join(self.output_loc, 'logs', log_filename)):
                with open(os.path.join(self.output_loc, 'logs', log_filename)) as f:
                    log_file = json.load(f)
            else:
                log_file = []
        else:
            log_file = use_file

        log_file.append(log_res)

        if log_to_file:
            with open(os.path.join(self.output_loc, 'logs', log_filename), 'w') as f:
                json.dump(log_file, f, indent=4)

        return log_file


