import matplotlib.pyplot as plt
import pandas as pd
import plot_fxn as plf
import seaborn as sns
import datetime
import os
import json


def mesh_plots(output_loc, plots_config):

    sns.set()
    fig = plt.figure(figsize=(15,9))

    if plots_config['ts']:
        ax1 = plt.subplot(321)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))
        plf.cycle_stats_plot(data, data_type='ts', subplot=True, ax=ax1)

    if plots_config['cfl']:
        ax2 = plt.subplot(323, sharex=ax1)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'cfl.csv'))
        plf.mesh_stats_plot(data, data_type='cfl', subplot=True, ax=ax2)

    if plots_config['min_div']:
        ax3 = plt.subplot(322, sharex=ax1)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'min_div.csv'))
        plf.mesh_stats_plot(data, data_type='min_div', subplot=True, ax=ax3)

    if plots_config['max_div']:
        ax4 = plt.subplot(324, sharex=ax1)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'max_div.csv'))
        plf.mesh_stats_plot(data, data_type = 'max_div', subplot = True, ax=ax4)

    if plots_config['ts_time']:
        ax5 = plt.subplot(325, sharex=ax1)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])
        plf.derived_cpu_step_plot(data, subplot=True, ax=ax5)

    if plots_config['vn']:
        ax6 = plt.subplot(326, sharex=ax1)
        data = pd.read_csv(os.path.join(output_loc, 'data', 'vn.csv'))
        plf.mesh_stats_plot(data, data_type='vn', subplot=True, ax=ax6)

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}', fontsize=12, va='top')
    plt.tight_layout()
    plt.savefig(os.path.join(output_loc, 'mesh_plots.png'), bbox_inches="tight")
    plt.show()


def sim_progress(output_loc, analytics_res):

    with open(os.path.join(output_loc, 'data', 'sim_info.json')) as f:
        sim_info = json.load(f)
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'), parse_dates=['log_time'])

    sns.set()
    fig = plt.figure(figsize=(15,9))

    widths = [1, 0.02, 1]
    heights = [0.01, 1, 0.005, 4]
    spec = fig.add_gridspec(ncols=3, nrows=4, width_ratios=widths, height_ratios=heights)

    ax1 = fig.add_subplot(spec[1, :])
    plf.timeprogress_bar_plot(data, sim_info, t_predict=analytics_res['runtime_pred']['pred'], subplot=True, ax=ax1)
    ax2 = fig.add_subplot(spec[3, 0])
    plf.log_interval_plot(data, subplot=True, ax=ax2)
    ax3 = fig.add_subplot(spec[3, 2], sharex=ax2)
    plf.comp_speed_plot(data, mAvg_spd=analytics_res['runtime_pred']['spd_info'], subplot=True, ax=ax3)

    fig.suptitle(f'{analytics_res["sim_status"]["stat"]}',
                 color=analytics_res["sim_status"]["color"],
                 fontsize=14,
                 va='top')

    plt.gcf().text(0.5, 0.94,
                   f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}',
                   fontsize=12,
                   ha='center', va='top',)

    plt.tight_layout()
    plt.savefig(os.path.join(output_loc, 'time_progress.png'), bbox_inches="tight")
    plt.show()


def cycle_plots(output_loc, plots_config):
    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))

    sns.set()
    fig = plt.figure(figsize=(15,9))

    widths = [1, 1]
    heights = [1, 1]
    spec = fig.add_gridspec(ncols=2, nrows=2, width_ratios=widths, height_ratios=heights)

    if plots_config['vel_err']:
        ax1 = fig.add_subplot(spec[0, 0])
        plf.cycle_stats_pm_plot(data, data_type='vel_err', subplot=True, ax=ax1)
    if plots_config['press_err']:
        ax2 = fig.add_subplot(spec[0, 1], sharex=ax1)
        plf.cycle_stats_pm_plot(data, data_type='press_err', subplot=True, ax=ax2)
    if plots_config['press_itr']:
        ax3 = fig.add_subplot(spec[1, 0], sharex=ax1)
        plf.press_itr_plot(data, subplot=True, ax=ax3)
    if plots_config['hrr']:
        ax4 = fig.add_subplot(spec[1, 1], sharex=ax1)
        plf.hrr_plot(os.path.join(output_loc, 'data'), subplot=True, ax=ax4)

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}',
                     fontsize=12, va='top')

    plt.savefig(os.path.join(output_loc, 'cycle_plots.png'), bbox_inches="tight")
    plt.show()


def plot(output_loc, plots_config, analytics_res):
    sim_progress(output_loc, analytics_res)
    mesh_plots(output_loc, plots_config)
    cycle_plots(output_loc, plots_config)

