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
    def __init__(self, output_loc, mavg_window, n_predictions, pred_status):
        self.mavg_window = mavg_window
        self.n_predictions = n_predictions
        self.output_loc = output_loc
        self.model_name = f'mAvg-{mavg_window}-v0.1.0'
        self.sim_end = None
        self.data = None
        self.pred_status = None
        self.is_delayed = False
        self.times_to_predict = None
        self.predictions = None
        self.conf_intervals = None
        self.avg_spd = None
        self.avg_spd_ci = None

        self.load_data()
        self.check_status(pred_status)

    def load_data(self):
        """Loads appropriate data for the model"""

        self.data = pd.read_csv(os.path.join(self.output_loc, 'data', 'cycle_info.csv'),
                                usecols=['log_time', 'sim_time'],
                                parse_dates=['log_time'])

        with open(os.path.join(self.output_loc, 'data', 'sim_info.json')) as f:
            sim_info = json.load(f)
        self.sim_end = sim_info['sim_end']

    def check_status(self, pred_status):

        if pred_status in ['err', 'compl']:
            self.pred_status = pred_status
            self.is_delayed = False
            return

        if len(self.data.index) < self.mavg_window:
            self.pred_status = 'no_data'
            self.is_delayed = False
            return

        if pred_status == 'delayed':
            self.pred_status = 'run'
            self.is_delayed = True
        else:
            self.pred_status = 'run'
            self.is_delayed = False
            return


    def get_times_to_predict(self):
        """The method calculates which times to predict"""

        time_range = np.linspace(0, self.sim_end, self.n_predictions)[1:]
        self.times_to_predict = time_range[time_range > self.data['sim_time'].iloc[-1]].astype(int)

    def calc_spd(self):
        """Calculates speeds"""

        self.data['time_diff'] = self.data['log_time'].diff().dt.total_seconds()
        self.data['sim_time_diff'] = self.data['sim_time'].diff()
        self.data['sim_speed'] = self.data['sim_time_diff'] / self.data['time_diff'] * 3600  # sims/h

        if self.pred_status == 'no_data':
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[0]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[0]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()

        else:
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[-self.mavg_window]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[-self.mavg_window]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()

    def estimate_predicted_times(self):

        t_deltas = (self.times_to_predict - self.data['sim_time'].iloc[-1]) / self.avg_spd
        self.predictions = [self.data['log_time'].iloc[-1] + timedelta(hours=k) for k in t_deltas]
        self.conf_intervals = t_deltas - (self.times_to_predict - self.data['sim_time'].iloc[-1]) / (self.avg_spd - self.avg_spd_ci)

    def predict(self):
        if self.pred_status in ['run', 'no_data']:
            self.calc_spd()
            self.get_times_to_predict()
            self.estimate_predicted_times()

    def report(self):

        rep_dict = {}
        rep_dict['m_name'] = self.model_name

        if self.pred_status == 'run':
            rep_dict['pred'] = []
            for time_pr, value_pr, interv_pr, in zip(self.times_to_predict, self.predictions, self.conf_intervals):
                res = {}
                res['t'] = time_pr
                res['pr_date'] = value_pr.strftime("%d-%b %H:%M")
                res['unc'] = round_to_hour_min(interv_pr)
                if time_pr < self.sim_end:
                    res['pr_type'] = 'mid'
                else:
                    res['pr_type'] = 'end'

                rep_dict['pred'].append(res)
            rep_dict['spd_info'] = f'MA speed: {self.avg_spd:.1f}\u00B1{self.avg_spd_ci:.1f} sim s/h'
            rep_dict['is_delayed'] = self.is_delayed

        elif self.pred_status == 'no_data':
            rep_dict['spd_info'] =f'MA speed: {self.avg_spd:.1f}\u00B1{self.avg_spd_ci:.1f} sim s/h\nLog entries less than moving {self.mavg_window} avg window!'
            rep_dict['pred'] = [{'t': self.sim_end,
                                  'pr_date': 'Insufficient\ndata',
                                  'pr_type': 'no_data'}]

        elif self.pred_status =='compl':
            rep_dict['pred'] = [{'t': self.data['sim_time'].iloc[-1],
                                 'pr_date': self.data['log_time'].iloc[-1].strftime("%d-%b %H:%M"),
                                 'pr_type': 'compl'}]
            rep_dict['spd_info'] = ''

        elif self.pred_status == 'err':
            rep_dict['pred'] = [{'t': self.data['sim_time'].iloc[-1],
                                 'pr_date': self.data['log_time'].iloc[-1].strftime("%d-%b %H:%M"),
                                 'pr_type': 'err'}]
            rep_dict['spd_info'] = ''

        return rep_dict


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


