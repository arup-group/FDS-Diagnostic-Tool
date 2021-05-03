import pandas as pd
import json
import os
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt

def load_data(output_loc):
    """Function loads relevant data"""

    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
    with open(os.path.join(output_loc, 'data', 'sim_info.json')) as f:
        sim_info = json.load(f)

    return data, sim_info

def get_times_to_predict(data, sim_info, n_predictions):
    """The method calculates which times to predict"""

    times_to_predict = np.linspace(0, sim_info['sim_end'], n_predictions)[1:]

    return times_to_predict[times_to_predict>data['sim_time'].iloc[-1]].astype(int)

def round_to_hour_min(time_interv):
    'Rounds confidence interval to h:min format'
    time_interv_sec = abs(time_interv*3600)
    hours, remainder = divmod(time_interv_sec, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f'{hours:.0f}:{int(minutes):02d}'


def report_results(times_predict, predicts_dt, pred_interv, sim_end):
    pred_res = []
    for time_pr, value_pr, interv_pr, in zip(times_predict, predicts_dt, pred_interv):
        res = {}
        res['t'] = time_pr
        res['pr_date'] = value_pr.strftime("%d-%b %H:%M")
        res['unc'] = round_to_hour_min(interv_pr)
        if time_pr < sim_end:
            res['pr_type'] = 'mid'
        else:
            res['pr_type'] = 'end'

        pred_res.append(res)

    return pred_res


def make_time_predictions(data, times_predict, mavg_window):

    data['time_diff'] = data['log_time'].diff().dt.total_seconds()
    data['sim_time_diff'] = data['sim_time'].diff()
    data['sim_speed'] = data['sim_time_diff'] / data['time_diff'] * 3600 # sims/h

    # Calculating average speed and conf interval
    dsimt = data['sim_time'].iloc[-1] - data['sim_time'].iloc[-mavg_window]
    dt = (data['log_time'].iloc[-1] - data['log_time'].iloc[-mavg_window]).total_seconds()
    avg_spd = dsimt/dt*3600
    conf_interv = 2*data['sim_speed'].iloc[-mavg_window:].std()

    # Calculating predictions
    predicts = (times_predict - data['sim_time'].iloc[-1])/avg_spd
    predicts_dt = [data['log_time'].iloc[-1]+timedelta(hours=k) for k in predicts]
    pred_interv = predicts - (times_predict - data['sim_time'].iloc[-1])/(avg_spd - conf_interv)

    return predicts_dt, pred_interv, avg_spd, conf_interv


#Parameters
output_loc = r'C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r1'

#Model hyper parameters
mavg_window = 30
n_predictions = 7

model_res = {}

data, sim_info = load_data(output_loc)
times_predict = get_times_to_predict(data, sim_info, n_predictions)

if times_predict !=[]:
    predicts_dt, pred_interv, model_res['avg_spd'], model_res['conf_itv'] = make_time_predictions(data, times_predict, mavg_window)
    model_res['pred'] = report_results(times_predict, predicts_dt, pred_interv, sim_info['sim_end'])

else:
    model_res['pred'] = [{'t': sim_info['sim_end'],
                          'pr_date': data['log_time'].iloc[-1].strftime("%d-%b %H:%M"),
                          'pr_type': 'compl'}]
    model_res['avg_spd'] = None
    model_res['conf_itv'] = None



print(model_res)

