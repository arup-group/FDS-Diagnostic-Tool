import pandas as pd
import os
import json

def analyse_run_status(data, sim_info, cur_time):
    """Function analyses simulation status based on defined conditions"""

    run_status = {}

    if sim_info['stop_cond'] == 'user':
        run_status['stat'] = 'Simulation Terminated by User'
        run_status['color'] = '#2CA02C'
        run_status['delay'] = None

    elif sim_info['stop_cond'] == 'instability':
        run_status['stat'] = 'Numerical Instability'
        run_status['color'] = '#C44E52'
        run_status['delay'] = None

    elif sim_info['stop_cond'] == 'completed':
        run_status['stat'] = 'Simulation Completed'
        run_status['color'] = '#2CA02C'
        run_status['delay'] = None

    else:
        if (cur_time - data['log_time'].iloc[-1]).total_seconds()/3600 > 24:
            run_status['stat'] = 'Simulation Interrupted'
            run_status['color'] = '#D62728'
        else:
            cur_diff = (cur_time - data['log_time'].iloc[-1]).total_seconds()
            last_entries_diff = data['log_time'].iloc[-31:].diff().dt.total_seconds()
            conf_interv = 2 * last_entries_diff.std()
            run_status['delay'] = (cur_diff - last_entries_diff.mean())

            if (cur_diff - last_entries_diff.mean()) > conf_interv:
                run_status['stat'] = 'Simulation Delayed'
                run_status['color'] = '#FF7F0E'
            else:
                run_status['stat'] = 'Simulation Running'
                run_status['color'] = '#2CA02C'

            run_status['delay'] = run_status['delay']/60

    return run_status


def load_data(output_loc):
    """Function loads relevant data"""

    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
    with open(os.path.join(output_loc, 'data', 'sim_info.json')) as f:
        sim_info = json.load(f)

    return data, sim_info

def status_prediction_main(output_loc, cur_time):

    data, sim_info = load_data(output_loc)
    run_status = analyse_run_status(data, sim_info, cur_time)

    return run_status