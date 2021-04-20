import matplotlib.pyplot as plt
import pandas as pd
import plot_fxn as plf
import seaborn as sns
import datetime
import os
import json

#TODO Update graph requirements as per key file
#TODO write main graph function
#TODO loc plots
#TODO main function controllin plots

def mesh_plots(output_loc):

    sns.set()
    fig = plt.figure(figsize=(15,9))

    ax1 = plt.subplot(321)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))
    plf.cycle_stats_plot(data, data_type='ts', subplot=True, ax=ax1)

    ax2 = plt.subplot(323, sharex=ax1)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cfl.csv'))
    plf.mesh_stats_plot(data, data_type='cfl', subplot=True, ax=ax2)

    ax3 = plt.subplot(322, sharex=ax1)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'min_div.csv'))
    plf.mesh_stats_plot(data, data_type='min_div', subplot=True, ax=ax3)
    #
    ax4 = plt.subplot(324, sharex=ax1)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'max_div.csv'))
    plf.mesh_stats_plot(data, data_type = 'max_div', subplot = True, ax=ax4)

    ax5 = plt.subplot(325, sharex=ax1)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
    plf.derived_cpu_step_plot(data, subplot=True, ax=ax5)

    ax6 = plt.subplot(326, sharex=ax1)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'vn.csv'))
    plf.mesh_stats_plot(data, data_type='vn', subplot=True, ax=ax6)

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}', fontsize=12, va='top')
    plt.tight_layout()
    plt.savefig(os.path.join(output_loc, 'mesh_plots.png'), bbox_inches="tight")
    plt.show()


def sim_progress(output_loc, analytics):

    with open(os.path.join(output_loc, 'data', 'sim_info.json')) as f:
        sim_info = json.load(f)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
    data = data.iloc[0:1000]

    sns.set()
    fig = plt.figure(figsize=(15,9))

    widths = [1,0.02, 1]
    heights = [1, 0.01, 4]
    spec = fig.add_gridspec(ncols=3, nrows=3, width_ratios=widths, height_ratios=heights)

    ax1 = fig.add_subplot(spec[0, :])
    plf.timeprogress_bar_plot(data, sim_info, t_predict=analytics["pred"], subplot=True, ax=ax1)
    ax2 = fig.add_subplot(spec[2, 0])
    plf.log_interval_plot(data, subplot=True, ax=ax2)
    ax3 = fig.add_subplot(spec[2, 2], sharex=ax2)
    plf.comp_speed_plot(data, subplot=True, ax=ax3)

    fig.suptitle(f'Sim Status: {analytics["status"]}\nLast Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}',
                 fontsize=12, va='top')

    plt.tight_layout()
    plt.savefig(os.path.join(output_loc, 'time_progress.png'), bbox_inches="tight")
    plt.show()


def cycle_plots(output_loc):
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))

    sns.set()
    fig = plt.figure(figsize=(15,9))

    widths = [1, 1]
    heights = [1, 1]
    spec = fig.add_gridspec(ncols=2, nrows=2, width_ratios=widths, height_ratios=heights)

    ax1 = fig.add_subplot(spec[0, 0])
    plf.cycle_stats_pm_plot(data, data_type='vel_err', subplot=True, ax=ax1)
    ax2 = fig.add_subplot(spec[0, 1], sharex=ax1)
    plf.cycle_stats_pm_plot(data, data_type='press_err', subplot=True, ax=ax2)
    ax3 = fig.add_subplot(spec[1, 0], sharex=ax1)
    plf.cycle_stats_plot(data, data_type='press_itr', subplot=True, ax=ax3)
    ax4 = fig.add_subplot(spec[1, 1], sharex=ax1)
    plf.hrr_plot(os.path.join(output_loc, 'data'), subplot=True, ax=ax4)

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}',
                     fontsize=12, va='top')

    plt.savefig(os.path.join(output_loc, 'cycle_plots.png'), bbox_inches="tight")
    plt.show()



# PARAMETERS
output_loc = r'C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r3'
mock_pred = [{'t': 400,
              'pr': '02-Apr 14:52',
              'unc': '1',
              'end': False},
             {'t': 600,
              'pr': '03-Apr 14:52',
              'unc': '1',
              'end': False},
             {'t': 800,
              'pr': '04-Apr 14:52',
              'unc': '1',
              'end': False},
             {'t': 1000,
              'pr': '05-Apr 14:52',
              'unc': '1',
              'end': False},
            {'t': 1200,
             'pr': '06-Apr 14:52',
             'unc': '1',
             'end': True}]
analytics = {'status': 'Running', 'pred': mock_pred}

sim_progress(output_loc, analytics)
mesh_plots(output_loc)
cycle_plots(output_loc)

# plf.timestep_bar_plot(data_loc, 'cpu_tot')
# plf.hrr_plot(data_loc)
# plf.general_stats_plot(data_loc, 'm_error')
# plf.general_stats_plot(data_loc, 'press_itr')