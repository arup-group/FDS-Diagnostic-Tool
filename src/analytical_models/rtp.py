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
    def __init__(self, output_loc, mavg_window, n_predictions):
        self.mavg_window = mavg_window
        self.n_predictions = n_predictions
        self.output_loc = output_loc
        self.model_name = f'mAvg-{mavg_window}'
        self.sim_end = None
        self.data = None
        self.enough_obsv = None
        self.times_to_predict = None
        self.predictions = None
        self.conf_intervals = None
        self.avg_spd = None
        self.avg_spd_ci = None

        self.load_data()
        self.check_data_len()

    def load_data(self):
        """Loads appropriate data for the model"""

        self.data = pd.read_csv(os.path.join(self.output_loc, 'data', 'cycle_info.csv'),
                                usecols=['log_time', 'sim_time'],
                                parse_dates=['log_time'])

        with open(os.path.join(self.output_loc, 'data', 'sim_info.json')) as f:
            sim_info = json.load(f)
        self.sim_end = sim_info['sim_end']

    def check_data_len(self):
        self. enough_obsv = len(self.data.index) > self.mavg_window

    def get_times_to_predict(self):
        """The method calculates which times to predict"""

        time_range = np.linspace(0, self.sim_end, self.n_predictions)[1:]
        self.times_to_predict = time_range[time_range > self.data['sim_time'].iloc[-1]].astype(int)

    def calc_spd(self):
        """Calculates speeds"""

        self.data['time_diff'] = self.data['log_time'].diff().dt.total_seconds()
        self.data['sim_time_diff'] = self.data['sim_time'].diff()
        self.data['sim_speed'] = self.data['sim_time_diff'] / self.data['time_diff'] * 3600  # sims/h

        if self.enough_obsv:
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[-self.mavg_window]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[-self.mavg_window]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()
        else:
            dsimt = self.data['sim_time'].iloc[-1] - self.data['sim_time'].iloc[0]
            dt = (self.data['log_time'].iloc[-1] - self.data['log_time'].iloc[0]).total_seconds()
            self.avg_spd = dsimt / dt * 3600
            self.avg_spd_ci = 2 * self.data['sim_speed'].iloc[-self.mavg_window:].std()

    def estimate_predicted_times(self):

        t_deltas = (self.times_to_predict - self.data['sim_time'].iloc[-1]) / self.avg_spd
        self.predictions = [self.data['log_time'].iloc[-1] + timedelta(hours=k) for k in t_deltas]
        self.conf_intervals = t_deltas - (self.times_to_predict - self.data['sim_time'].iloc[-1]) / (self.avg_spd - self.avg_spd_ci)

    def predict(self):
        self.get_times_to_predict()
        self.calc_spd()
        self.estimate_predicted_times()

    def report(self):

        rep_dict = {}
        rep_dict['m_name'] = self.model_name
        if self.enough_obsv:
            if self.times_to_predict != []:
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

            else:
                rep_dict['pred'] = [{'t': self.sim_end,
                                      'pr_date': self.data['log_time'].iloc[-1].strftime("%d-%b %H:%M"),
                                      'pr_type': 'compl'}]
                rep_dict['spd_info'] = ''


        else:
            rep_dict['spd_info'] =f'MA speed: {self.avg_spd:.1f}\u00B1{self.avg_spd_ci:.1f} sim s/h\nLog entries less than moving {self.mavg_window} avg window!'
            rep_dict['pred'] = [{'t': self.sim_end,
                                  'pr_date': 'Insufficient data',
                                  'pr_type': 'compl'}]

        return rep_dict


    def log(self):
        pass

