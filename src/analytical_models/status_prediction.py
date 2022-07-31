import pandas as pd
import os
import json


class predictSimStatus():

    def __init__(self, output_loc, cur_time):

        self.output_loc = output_loc
        self.sim_info_data = None
        self.cycle_info_data = None
        self.cur_time = cur_time

        self.results = {}

        self._load_data()
        self._calc_last_log_time_diff()
        self._calc_avg_output_frequency()
        self._predict_status()
            
    def _load_data(self):
        """Function loads relevant data"""
        self.cycle_info_data = pd.read_csv(
            os.path.join(self.output_loc, 'data', 'cycle_info.csv'),
            parse_dates=['log_time'])
        with open(os.path.join(self.output_loc, 'data', 'sim_info.json')) as f:
            self.sim_info_data = json.load(f)

    def _predict_status(self):
        """Possible - running, completed, instability, stopped, delayed, stalled"""

        if self.sim_info_data['stop_cond'] == 'user':
            self.results['status'] = 'stopped'
            self.results['is_dot_stop'] = True
            self.results['is_error'] = False
            self.results['is_delayed'] = False

        elif self.sim_info_data['stop_cond'] == 'instability':
            self.results['status'] = 'instability'
            self.results['is_dot_stop'] = False
            self.results['is_error'] = True
            self.results['is_delayed'] = False

        elif self.sim_info_data['stop_cond'] == 'completed':
            self.results['status'] = 'completed'
            self.results['is_dot_stop'] = False
            self. results['is_error'] = False
            self.results['is_delayed'] = False

        elif self.last_log_diff / 3600 > 24:
            self.results['status'] = 'stalled'
            self.results['is_dot_stop'] = False
            self.results['is_error'] = True
            self.results['is_delayed'] = True

        elif (self.last_log_diff - self.outp_freq_mean) > self.outp_freq_conf:
            self.results['status'] = 'running'
            self.results['is_dot_stop'] = False
            self.results['is_error'] = False
            self.results['is_delayed'] = True

        else:
            self.results['status'] = 'running'
            self.results['is_dot_stop'] = False
            self.results['is_error'] = False
            self.results['is_delayed'] = False

    def _calc_last_log_time_diff(self):
        self.last_log_diff = (self.cur_time - self.cycle_info_data['log_time'].iloc[-1]).total_seconds()

    def _calc_avg_output_frequency(self):
        last_entries = self.cycle_info_data['log_time'].iloc[-31:].diff().dt.total_seconds()
        self.outp_freq_conf = 2 * last_entries.std()
        self.outp_freq_mean = last_entries.mean()

    def report_status(self):
        self.results['outp_freq_mean'] = round(self.outp_freq_mean, 0)
        self.results['outp_freq_conf'] = round(self.outp_freq_conf, 0)
        self.results['last_log_diff'] = round(self.last_log_diff, 0)
        self.results['last_log_time'] = self.sim_info_data['lst_log_time']
        return self.results

    def _delete_data(self):
        pass


#OLD TO BE REMOVED
# def analyse_run_status(data, sim_info, cur_time):
#     """Function analyses simulation status based on defined conditions"""
#
#     run_status = {}
#
#     if sim_info['stop_cond'] == 'user':
#         run_status['stat_msg'] = 'Simulation Terminated by User'
#         run_status['stat'] = 'compl'
#         run_status['color'] = '#2CA02C'
#         run_status['delay'] = None
#
#     elif sim_info['stop_cond'] == 'instability':
#         run_status['stat_msg'] = 'Numerical Instability'
#         run_status['stat'] = 'err'
#         run_status['color'] = '#C44E52'
#         run_status['delay'] = None
#
#     elif sim_info['stop_cond'] == 'completed':
#         run_status['stat_msg'] = 'Simulation Completed'
#         run_status['stat'] = 'compl'
#         run_status['color'] = '#2CA02C'
#         run_status['delay'] = None
#
#     else:
#         if (cur_time - data['log_time'].iloc[-1]).total_seconds()/3600 > 24:
#             run_status['stat_msg'] = 'Simulation Interrupted'
#             run_status['stat'] = 'err'
#             run_status['color'] = '#D62728'
#         else:
#             cur_diff = (cur_time - data['log_time'].iloc[-1]).total_seconds()
#             last_entries_diff = data['log_time'].iloc[-31:].diff().dt.total_seconds()
#             conf_interv = 2 * last_entries_diff.std()
#             run_status['delay'] = (cur_diff - last_entries_diff.mean())
#
#             if (cur_diff - last_entries_diff.mean()) > conf_interv:
#                 run_status['stat_msg'] = 'Simulation Delayed'
#                 run_status['stat'] = 'delayed'
#                 run_status['color'] = '#FF7F0E'
#             else:
#                 run_status['stat_msg'] = 'Simulation Running'
#                 run_status['stat'] = 'run'
#                 run_status['color'] = '#2CA02C'
#
#             run_status['delay'] = run_status['delay']/60
#
#     run_status['lst_sim_time'] = data['sim_time'].iloc[-1]
#     run_status['lst_log_time'] = data['log_time'].iloc[-1].strftime("%d-%b %H:%M")
#
#     return run_status
#
#
# def load_data(output_loc):
#     """Function loads relevant data"""
#
#     data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
#     with open(os.path.join(output_loc, 'data', 'sim_info.json')) as f:
#         sim_info = json.load(f)
#
#     return data, sim_info
#
# def status_prediction_main(output_loc, cur_time):
#
#     data, sim_info = load_data(output_loc)
#     run_status = analyse_run_status(data, sim_info, cur_time)
#
#     return run_status