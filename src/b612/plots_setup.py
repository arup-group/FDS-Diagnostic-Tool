import matplotlib.pyplot as plt
import pandas as pd
import plot_fxn as plf
import seaborn as sns
import datetime
import os
import json
import logging


def mesh_plots(output_loc, plots_config):
    logger = logging.getLogger('sim_log')

    sns.set()
    fig = plt.figure(figsize=(15,9))

    if plots_config['ts']:
        try:
            ax1 = plt.subplot(321)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))
            plf.cycle_stats_plot(data, data_type='ts', subplot=True, ax=ax1)
        except:
            logger.exception('Error in timestep plot.')

    if plots_config['cfl']:
        try:
            ax2 = plt.subplot(323, sharex=ax1)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'cfl.csv'))
            plf.mesh_stats_plot(data, data_type='cfl', subplot=True, ax=ax2)
        except:
            logger.exception('Error in CFL plot.')

    if plots_config['min_div']:
        try:
            ax3 = plt.subplot(322, sharex=ax1)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'min_div.csv'))
            plf.mesh_stats_plot(data, data_type='min_div', subplot=True, ax=ax3)
        except:
            logger.exception('Error with min div plot.')

    if plots_config['max_div']:
        try:
            ax4 = plt.subplot(324, sharex=ax1)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'max_div.csv'))
            plf.mesh_stats_plot(data, data_type = 'max_div', subplot = True, ax=ax4)
        except:
            logger.exception('Error with max div plot.')

    if plots_config['ts_time']:
        try:
            ax5 = plt.subplot(325, sharex=ax1)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'cpu_step.csv'), parse_dates=['log_time'])
            plf.mesh_stats_plot(data, data_type='cpu_step', subplot=True, ax=ax5)
        except:
            logger.exception('Error with VN plot.')

    if plots_config['vn']:
        try:
            ax6 = plt.subplot(326, sharex=ax1)
            data = pd.read_csv(os.path.join(output_loc, 'data', 'vn.csv'))
            plf.mesh_stats_plot(data, data_type='vn', subplot=True, ax=ax6)
        except:
            logger.exception('Error with VN plot.')

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
    plf.timeprogress_bar_plot(data, sim_info, t_predict=analytics_res['runtime_pred'], subplot=True, ax=ax1)
    ax2 = fig.add_subplot(spec[3, 0])
    plf.log_interval_plot(data, subplot=True, ax=ax2)
    ax3 = fig.add_subplot(spec[3, 2], sharex=ax2)
    plf.comp_speed_plot(data, mAvg_spd=analytics_res['runtime_pred']['spd_info'], subplot=True, ax=ax3)

    fig.suptitle(f'{analytics_res["sim_status"]["stat_msg"]}',
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
    logger = logging.getLogger('sim_log')

    data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))

    sns.set()
    fig = plt.figure(figsize=(15,9))

    widths = [1, 1]
    heights = [1, 1]
    spec = fig.add_gridspec(ncols=2, nrows=2, width_ratios=widths, height_ratios=heights)

    if plots_config['vel_err']:
        try:
            ax1 = fig.add_subplot(spec[0, 0])
            plf.cycle_stats_pm_plot(data, data_type='vel_err', subplot=True, ax=ax1)
        except:
            logger.exception('Error with velocity error plot.')

    if plots_config['press_itr']:
        try:
            ax2 = fig.add_subplot(spec[0, 1], sharex=ax1)
            plf.press_itr_plot(data, subplot=True, ax=ax2)
        except:
            logger.exception('Error with pressure iterations plot.')

    if plots_config['hrr']:
        try:
            ax3 = fig.add_subplot(spec[1, :])
            plf.hrr_plot(os.path.join(output_loc, 'data'), subplot=True, ax=ax3)
        except:
            logger.exception('Error with HRR plot.')

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}',
                     fontsize=12, va='top')

    plt.savefig(os.path.join(output_loc, 'cycle_plots.png'), bbox_inches="tight")
    plt.show()


def loc_plots(output_loc, plots_config):
    logger = logging.getLogger('sim_log')

    # Check if image data present. If not raise warning and exit
    if not os.path.isfile(os.path.join(output_loc, 'imgs', 'xy.png')):
        logger.warning('Image data not present. Cannot process location plots.')
        return

    #Check if you mesh data can be loaded. If not return error and exit
    try:
        with open(os.path.join(output_loc, 'data', 'mesh_data.json'), 'r') as fp:
            mesh_data = json.load(fp)
    except:
        logger.exception('Error with loading mesh data.')

    last_points = plots_config['last_loc_pts']
    which_mesh = 'max'

    if plots_config['vn_loc']:
        try:
            data = pd.read_csv(os.path.join(output_loc, 'data', 'vn.csv'))
            plf.plot_loc(data, mesh_data, 'vn', last_points, which_mesh, output_loc)
        except:
            logger.exception('Error with VN location plot.')

    if plots_config['max_div_loc']:
        try:
            data = pd.read_csv(os.path.join(output_loc, 'data', 'max_div.csv'))
            plf.plot_loc(data, mesh_data, 'max_div', last_points, which_mesh, output_loc)
        except:
            logger.exception('Error with max div location plot.')

    if plots_config['min_div_loc']:
        try:
            data = pd.read_csv(os.path.join(output_loc, 'data', 'min_div.csv'))
            plf.plot_loc(data, mesh_data, 'min_div', last_points, which_mesh, output_loc)
        except:
            logger.exception('Error with min div location plot.')

    if plots_config['cfl_loc']:
        try:
            data = pd.read_csv(os.path.join(output_loc, 'data', 'cfl.csv'))
            plf.plot_loc(data, mesh_data, 'cfl', last_points, which_mesh, output_loc)
        except:
            logger.exception('Error with CFL location plot.')

    if plots_config['vel_err_loc']:
        try:
            data = pd.read_csv(os.path.join(output_loc, 'data', 'cycle_info.csv'))
            plf.plot_loc(data, mesh_data, 'vel_err', last_points, which_mesh, output_loc)
        except:
            logger.exception('Error with vel error location plot.')


def plot(output_loc, plots_config, analytics_res):
    logger = logging.getLogger('sim_log')

    if plots_config['time_progress']:
        try:
            sim_progress(output_loc, analytics_res)
        except:
            logger.exception('Error in simulation progression plot.')

    if any([plots_config[k] for k in ['min_div', 'max_div', 'vn', 'cfl', 'ts', 'ts_time']]):
        mesh_plots(output_loc, plots_config)

    if any([plots_config[k] for k in ['vel_err', 'press_itr', 'hrr']]):
        cycle_plots(output_loc, plots_config)

    loc_plots(output_loc, plots_config)