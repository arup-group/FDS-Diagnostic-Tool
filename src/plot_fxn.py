import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from PIL import Image
import os
import re
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from matplotlib.ticker import AutoMinorLocator
import logging


def day_rounder(date_min, type_round, h_intv):
    ''''Rounds axis times when timedate objects are used'''

    if type_round == 'd':
        if date_min.hour < 12:
            date_min = date_min.replace(second=0, microsecond=0, minute=0, hour=0)
        else:
            date_min = date_min.replace(second=0, microsecond=0, minute=0, hour=12)

        date_max = date_min + timedelta(hours=int(h_intv) + 12)

    elif type_round == 'h':
        min_to_round = date_min.minute - date_min.minute % 10
        date_min = date_min.replace(second=0, microsecond=0, minute=min_to_round)
        date_max = date_min + timedelta(hours=int(h_intv) + 0.166)

    return date_min, date_max


def format_ax(data, ax, total_time_span):

    ax_data = {'1': {'ML_fxn': mdates.MinuteLocator,
                     'itv': 10,
                     'mL': 5,
                     'fmt': '%H:%M',
                     'rnd': 'h',
                     'gr_sp': '2 min'},
               '6': {'ML_fxn': mdates.MinuteLocator,
                     'itv': 60,
                     'mL': 4,
                     'fmt': '%H:%M',
                     'rnd': 'h',
                     'gr_sp': '15 min'},
               '24': {'ML_fxn': mdates.HourLocator,
                      'itv': 6,
                      'mL': 6,
                      'fmt': '%d %Hh',
                      'rnd': 'h',
                      'gr_sp': '1 h'},
               '96': {'ML_fxn': mdates.HourLocator,
                      'itv': 8,
                      'mL': 2,
                      'fmt': '%d %Hh',
                      'rnd': 'd',
                      'gr_sp': '4 h'},
               '192': {'ML_fxn': mdates.DayLocator,
                       'itv': 1,
                       'mL': 4,
                       'fmt': '%d-%b',
                       'rnd': 'd',
                       'gr_sp': '6 h'},
               '288': {'ML_fxn': mdates.DayLocator,
                       'itv': 2,
                       'mL': 4,
                       'fmt': '%d-%b',
                       'rnd': 'd',
                       'gr_sp': '12 h'},
               '384': {'ML_fxn': mdates.DayLocator,
                       'itv': 2,
                       'mL': 4,
                       'fmt': '%d-%b',
                       'rnd': 'd',
                       'gr_sp': '12 d'},
               '768': {'ML_fxn': mdates.DayLocator,
                            'itv': 4,
                            'mL': 4,
                            'fmt': '%d-%b',
                            'rnd': 'd',
                            'gr_sp': '1 d'},
               '1536': {'ML_fxn': mdates.DayLocator,
                       'itv': 8,
                       'mL': 4,
                       'fmt': '%d-%b',
                       'rnd': 'd',
                       'gr_sp': '2 d'}
               }

    for tdiff in [1, 6, 24, 96, 192, 288, 384, 768, 1536]:
        if total_time_span < tdiff:
            tdiff = str(tdiff)

            datemin, datemax = day_rounder(data['log_time'].iloc[0], ax_data[tdiff]['rnd'], tdiff)
            ax.set_xlim(datemin, datemax)

            # Set major ticks
            fmt_x_axis = ax_data[tdiff]['ML_fxn'](interval=ax_data[tdiff]['itv'])
            ax.xaxis.set_major_locator(fmt_x_axis)
            ax.xaxis.set_major_formatter(mdates.DateFormatter(ax_data[tdiff]['fmt']))

            # Set minor ticks
            ax.xaxis.set_minor_locator(AutoMinorLocator(ax_data[tdiff]['mL']))

            # Set text
            ax.text(0.98, 0.02, f"Grid scale: {ax_data[tdiff]['gr_sp']}",
                    ha='right', va='bottom', transform=ax.transAxes, size=11)

            break


def mesh_stats_plot(data, data_type, subplot=False, ax=None):
    # Function starts here
    plot_type = {'min_div': ['Min divergence', 'Simulation time (s)'],
                 'max_div': ['Max divergence', 'Simulation time (s)'],
                 'cfl': ['CFL number', 'Simulation time (s)'],
                 'vn': ['VN number', 'Simulation time (s)'],
                 'cpu_step': ['Max time per timestep (s)', 'Simulation time (s)']}

    r = re.compile('^m\d+$')
    sorted_columns = list(filter(r.match, list(data.columns)))

    data['est'] = data[sorted_columns].max(axis=1)
    data['mesh'] = data[sorted_columns].idxmax(axis=1)

    if data_type == 'min_div':
        data['est'] = data[sorted_columns].min(axis=1)
        data['mesh'] = data[sorted_columns].idxmin(axis=1)

    plot_data = {}

    # Assign colors
    colors = sns.color_palette()
    colors_dict = {}
    k = 0
    for i, entry in data['mesh'].value_counts().iteritems():
        if k > 9:
            colors_dict[i] = colors[9]
        else:
            colors_dict[i] = colors[k]
        k = k + 1

    for k, mesh in enumerate(data['mesh'].unique()):

        list_dicts = []
        plot_dict = {}

        index_sorted = data[data['mesh'] == mesh].index.values
        diff_index = np.diff(index_sorted)
        res = np.where(diff_index > 1)

        if len(index_sorted) > 1:
            if res[0].size == 0:
                plot_dict['start'] = index_sorted[0]
                plot_dict['end'] = index_sorted[-1]
                list_dicts.append(plot_dict)

            else:
                for k, index in enumerate(res[0]):
                    if k == 0:
                        plot_dict['start'] = index_sorted[0]
                        plot_dict['end'] = index_sorted[index]

                    else:
                        plot_dict['start'] = index_sorted[res[0][k - 1] + 1]
                        plot_dict['end'] = index_sorted[index]

                    list_dicts.append(plot_dict)
                    plot_dict = {}

                # Final curve segment
                plot_dict['start'] = index_sorted[res[0][-1] + 1]
                plot_dict['end'] = index_sorted[-1]
                list_dicts.append(plot_dict)

        else:
            plot_dict['start'] = index_sorted[0]
            plot_dict['end'] = index_sorted[0]
            list_dicts.append(plot_dict)

        plot_data[mesh] = list_dicts

    if subplot == False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    for mesh in plot_data:
        for k in plot_data[mesh]:
            x = data.loc[k['start']:k['end'], 'sim_time']
            y = data.loc[k['start']:k['end'], 'est']

            if k['start'] != 0:
                x = x.append(
                    pd.Series(0.5 * (data.loc[k['start'], 'sim_time'] + data.loc[k['start'] - 1, 'sim_time'])))

            if k['end'] != data.index.max():
                x = x.append(0.5 * (pd.Series(data.loc[k['end'], 'sim_time'] + data.loc[k['end'] + 1, 'sim_time'])))

            if k['start'] != 0:
                y = y.append(0.5 * (pd.Series(data.loc[k['start'], 'est'] + data.loc[k['start'] - 1, 'est'])))

            if k['end'] != data.index.max():
                y = y.append(0.5 * (pd.Series(data.loc[k['end'], 'est'] + data.loc[k['end'] + 1, 'est'])))

            new_x, new_y = zip(*sorted(zip(x, y)))
            ax = plt.plot(new_x, new_y, '-', color=colors_dict[mesh], label=mesh)

    # Legend setup
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax = plt.legend(by_label.values(), by_label.keys(), ncol=4, loc=4)
    ax = plt.xlabel(plot_type[data_type][1])
    ax = plt.ylabel(plot_type[data_type][0])

    if data_type == 'cpu_step':
        ax = plt.ylim([0, data['est'].mean() + 5 * data['est'].std()])


def cycle_stats_pm_plot(data, data_type, subplot=False, ax=None):
    logger = logging.getLogger('sim_log')

    # Function starts here
    plot_type = {'vel_err': ['Velocity error (m/s)', 'Simulation time (s)'],
                 'press_err': ['Pressure error', 'Simulation time (s)']}


    data['est'] = data[data_type]
    data['mesh'] = data[f'{data_type}_m']

    if data['est'].isnull().any():
        logger.warning(f'NaN values in {data_type} data. Removing them before plotting.')
        data = data.dropna(subset=['est'])
        data = data.reset_index(drop=True)


    plot_data = {}

    # Assign colors
    colors = sns.color_palette()
    colors_dict = {}
    k = 0
    for i, entry in data['mesh'].value_counts().iteritems():
        if k > 9:
            colors_dict[i] = colors[9]
        else:
            colors_dict[i] = colors[k]
        k = k + 1

    for k, mesh in enumerate(data['mesh'].unique()):

        list_dicts = []
        plot_dict = {}

        index_sorted = data[data['mesh'] == mesh].index.values
        diff_index = np.diff(index_sorted)
        res = np.where(diff_index > 1)

        if len(index_sorted) > 1:
            if res[0].size == 0:
                plot_dict['start'] = index_sorted[0]
                plot_dict['end'] = index_sorted[-1]
                list_dicts.append(plot_dict)

            else:
                for k, index in enumerate(res[0]):
                    if k == 0:
                        plot_dict['start'] = index_sorted[0]
                        plot_dict['end'] = index_sorted[index]

                    else:
                        plot_dict['start'] = index_sorted[res[0][k - 1] + 1]
                        plot_dict['end'] = index_sorted[index]

                    list_dicts.append(plot_dict)
                    plot_dict = {}

                # Final curve segment
                plot_dict['start'] = index_sorted[res[0][-1] + 1]
                plot_dict['end'] = index_sorted[-1]
                list_dicts.append(plot_dict)

        else:
            plot_dict['start'] = index_sorted[0]
            plot_dict['end'] = index_sorted[0]
            list_dicts.append(plot_dict)

        plot_data[mesh] = list_dicts

    if subplot == False:
        sns.set()
        fig, ax = plt.subplots(figsize=(15, 6))

    for mesh in plot_data:
        for k in plot_data[mesh]:
            x = data.loc[k['start']:k['end'], 'sim_time']
            y = data.loc[k['start']:k['end'], 'est']

            if k['start'] != 0:
                x = x.append(
                    pd.Series(0.5 * (data.loc[k['start'], 'sim_time'] + data.loc[k['start'] - 1, 'sim_time'])))

            if k['end'] != data.index.max():
                x = x.append(0.5 * (pd.Series(data.loc[k['end'], 'sim_time'] + data.loc[k['end'] + 1, 'sim_time'])))

            if k['start'] != 0:
                y = y.append(0.5 * (pd.Series(data.loc[k['start'], 'est'] + data.loc[k['start'] - 1, 'est'])))

            if k['end'] != data.index.max():
                y = y.append(0.5 * (pd.Series(data.loc[k['end'], 'est'] + data.loc[k['end'] + 1, 'est'])))

            new_x, new_y = zip(*sorted(zip(x, y)))
            ax = plt.plot(new_x, new_y, '-', color=colors_dict[mesh], label=mesh)

    # Legend setup
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax = plt.legend(by_label.values(), by_label.keys(), ncol=4, loc=4)
    ax = plt.xlabel(plot_type[data_type][1])
    ax = plt.ylabel(plot_type[data_type][0])

    if subplot == False:
        ax.plot()


def cycle_stats_plot(data, data_type, subplot=False, ax=None):
    # Function starts here
    plot_type = {'ts': ['Time step (s)', 'Simulation time (s)'],
                 'vel_err': ['Velocity error', 'Simulation time (s)'],
                 'press_itr': ['Pressure', 'Simulation time (s)'],
                 'press_err': ['Pressure error', 'Simulation time (s)']}


    if subplot == False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    colors = sns.color_palette()
    ax = plt.plot(data['sim_time'], data[data_type], '-', color=colors[0], label=data_type)
    ax = plt.xlabel(plot_type[data_type][1])
    ax = plt.ylabel(plot_type[data_type][0])
    return data


def timestep_bar_plot(data, output_loc, show_debug):

    r = re.compile('^m\d+$')
    sorted_columns = list(filter(r.match, list(data.columns)))

    performance = data[sorted_columns].max().sort_values()/3600
    y_pos = np.arange(len(performance))
    objects = list(performance.index)

    fig, ax = plt.subplots(figsize=(15, 6))

    plt.barh(y_pos, performance, align='center', alpha=0.8)
    plt.yticks(y_pos, objects)
    plt.xlabel('Total time (h)')
    fig.suptitle(f'MPI Usage\nLast Updated: {datetime.now().strftime("%d-%b-%Y %H:%M")}',
                 fontsize=12, va='top')
    plt.savefig(os.path.join(output_loc, f'cpu_use.png'), bbox_inches="tight")
    if show_debug:
        plt.show()
    plt.close(fig)

    return


def lagrange_plot(data_loc):
    data = pd.read_csv(os.path.join(data_loc, 'lagrange.csv'))
    r = re.compile('^m\d+$')

    sorted_columns = list(filter(r.match, list(data.columns)))
    data['est'] = data[sorted_columns].max(axis=1)

    fig, ax = plt.subplots(figsize=(15, 6))
    sns.set()
    colors = sns.color_palette()
    ax = plt.plot(data['sim_time'], data['est'], '-', color=colors[0])
    ax = plt.ylabel('Lagrange particles')
    ax = plt.xlabel('Simulation time (s)')

    return data


def hrr_plot(data_loc, subplot=False, ax=None):
    logger = logging.getLogger('sim_log')

    data_hrr = pd.read_csv(os.path.join(data_loc, 'hrr.csv'))
    nrg_loss = pd.read_csv(os.path.join(data_loc, 'nrg_loss.csv'))

    r = re.compile('^m\d+$')

    sorted_columns = list(filter(r.match, list(data_hrr.columns)))
    data_hrr['est'] = data_hrr[sorted_columns].sum(axis=1)
    sorted_columns = list(filter(r.match, list(nrg_loss.columns)))
    nrg_loss['est'] = nrg_loss[sorted_columns].sum(axis=1)

    if subplot is False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    ax = plt.plot(data_hrr['sim_time'], data_hrr['est'], '-', color='#4C72B0', label='HRR output')
    ax = plt.plot(data_hrr['sim_time'], nrg_loss['est'].abs(), '-', color='#DD8452', label='Rad. loss')

    try:
        fire_curve = pd.read_csv(os.path.join(data_loc, 'hrr_curve.csv'))
        ax = plt.plot(fire_curve['t'], fire_curve['HRR'], '--', color='red', label='HRR definition')
    except:
        logger.warning(f'HRR curve unable to load.')
        pass

    ax = plt.xlim(0, data_hrr['sim_time'].max() + 20)
    ax = plt.ylabel('Total energy (KW)')
    ax = plt.xlabel('Simulation time (s)')
    ax = plt.legend()

    if subplot is False:
        plt.show()


def derived_cpu_step_plot(data, subplot=False, ax=None):
    """Time step/time plot derived from avaliable data - used for b673 built"""

    data['time_diff'] = data['log_time'].diff().dt.total_seconds()
    data['cycle_diff'] = data['cycles'].diff()
    data['step_time'] = data['time_diff'] / data['cycle_diff']

    if subplot == False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    ax = plt.plot(data['sim_time'], data['step_time'], '-', label='ts')
    ax = plt.xlabel('Simulation time (s)')
    ax = plt.ylabel('Time per time step (s)')


def log_interval_plot(data, subplot=False, ax=None):

    data['time_diff'] = data['log_time'].diff().dt.total_seconds()
    data['sim_time_diff'] = data['sim_time'].diff()
    total_time_span = (data['log_time'].iloc[-1] - data['log_time'].iloc[0]).total_seconds()/3600


    if subplot == False:
        sns.set()
        fig, ax = plt.subplots()


    p1, = ax.plot(data['log_time'], data['time_diff']/60, '-', color='#4C72B0', label='log interv.')
    twin1 = ax.twinx()
    p2, = twin1.plot(data['log_time'], data['sim_time_diff'], '-', color='#DD8452', label='sim time incr.')

    # Format axis
    format_ax(data, ax, total_time_span)
    # format_ax(data, twin1, total_time_span)

    ax.set_xlabel('Log time')
    ax.set_ylabel('Log intervals (min)')
    twin1.set_ylabel('Sim time increments (s)')
    ax.xaxis.set_tick_params(rotation=30)
    twin1.grid(None)
    ax.grid(b=True, which='major', linewidth=1.6)
    ax.grid(b=True, which='minor', linewidth=0.6)

    ax.legend(handles=[p1, p2])

    plt.tight_layout()

    if subplot == False:
        plt.show()


def comp_speed_plot(data, mAvg_spd=False, subplot=False, ax=None):

    data['time_diff'] = data['log_time'].diff().dt.total_seconds()
    data['sim_time_diff'] = data['sim_time'].diff()
    data['sim_speed'] = data['sim_time_diff'] / data['time_diff'] * 3600 # sims/h
    total_time_span = (data['log_time'].iloc[-1] - data['log_time'].iloc[0]).total_seconds()/3600


    if subplot == False:
        sns.set()
        fig, ax = plt.subplots()


    ax.plot(data['log_time'], data['sim_speed'], '-')

    # Format axis
    format_ax(data, ax, total_time_span)

    ax.grid(b=True, which='major', linewidth=1.6)
    ax.grid(b=True, which='minor', linewidth=0.6)

    y_max = data['sim_speed'].mean() + 3 * data['sim_speed'].std()
    if y_max > data['sim_speed'].max() + 10:
        y_max = data['sim_speed'].max() + 10
    ax.set_ylim(0, y_max)

    if mAvg_spd:
        ax.text(0.98, 0.96, mAvg_spd, ha='right', va='top', transform=ax.transAxes, size=11)

    plt.xlabel('Log time')
    plt.ylabel('Simulation speed (sim s/h)')
    plt.xticks(rotation=30)
    plt.tight_layout()



    if subplot == False:
        plt.show()


def timeprogress_bar_plot(data, sim_info, t_predict=False, subplot=False, ax=None):

    date_start = datetime.strptime(sim_info["date_start"], "%B %d, %Y %H:%M:%S")

    if subplot == False:
        sns.set()
        fig, ax = plt.subplots(figsize=(15,2))

    # Plot bar progression
    ax.barh(1, data['sim_time'].max(), height=1, align='center', alpha=0.4)
    ax.barh(1, sim_info["sim_end"], height=1, edgecolor='#4C72B0', linewidth=1, fill=False, align='center')

    #Plot start time
    ax.plot([1,1], [0.5, 1.5], color='#4C72B0', linewidth=4)
    ax.text(10,1, f'Start\n{date_start.strftime("%d-%b %H:%M")}', va='center')

    #Plot predictons

    if t_predict:

        for i in t_predict['pred']:
            if i['pr_type'] is 'end':
                if t_predict['is_delayed']:
                    ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed',  color='#DD8452', linewidth=2)
                else:
                    ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed', color='#2CA02C', linewidth=2)
                ax.text(i['t']+9, 1, f'Complete\n{i["pr_date"]}\n($\pm${i["unc"]}h)', va='center', size=11)

            elif i['pr_type'] is 'compl':
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='solid',  color='#2CA02C', linewidth=2)
                ax.text(i['t']+9, 1, f'Completed\n{i["pr_date"]}', va='center', size=11)

            elif i['pr_type'] is 'no_data':
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed',  color='#DD8452', linewidth=2)
                ax.text(i['t']+9, 1, f'Complete\n{i["pr_date"]}', va='center', size=11)

            elif i['pr_type'] is 'err':
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='solid',  color='#C44E52', linewidth=2)
                ax.text(i['t']+9, 1, f'Last log\n{i["pr_date"]}', va='center', size=11)

            elif i['pr_type'] is 'mid':
                if t_predict['is_delayed']:
                    ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed', color='#DD8452', linewidth=2)
                else:
                    ax.plot([i['t'], i['t']], [0.5, 1.5],linestyle='dashed',  color='#2CA02C', linewidth=2)
                ax.text(i['t']+9, 1, f'{i["pr_date"]}\n($\pm${i["unc"]}h)', va='center', size=11)




    ax.set_xlim([0, sim_info["sim_end"]+100])
    ax.set_xticks(np.arange(0, sim_info["sim_end"] + 100, 100))
    ax.set_ylim([0.45, 1.55])
    ax.set_xlabel('Simulation time progress (s)')
    ax.set_yticks([])
    ax.grid(b=True, which='major', linewidth=1.6)

    if subplot == False:
        plt.show()

    return


def press_itr_plot(data, subplot=False, ax=None):

    if subplot == False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    colors = sns.color_palette()
    ax.fill_between(data['sim_time'], 0, data['press_itr'], color=colors[0])
    ax.set_ylim(0, 10.5)
    ax.set_yticks(np.arange(0, 10.5, 1))
    ax = plt.xlabel('Simulation time (s)')
    ax = plt.ylabel('Pressure iterations')

    return data


def plot_loc(data, mesh_data, data_type, last_points, which_mesh, output_loc, show_debug):

    def calc_sizes(size_dict, spacing=0.05, hor_mar=0.05, ver_mar=0.05):
        # Check size

        dx_m = size_dict['dx']
        dy_m = size_dict['dy']
        dz_m = size_dict['dz']

        if dx_m > dy_m:
            width = (0.98 - 2 * hor_mar - spacing) * dx_m / (dx_m + dz_m)
            z_height = (1 - 2 * hor_mar - spacing) * dz_m / (dx_m + dz_m)
            height = width * dy_m / dx_m
        else:
            height = (1 - 2 * ver_mar - spacing) * dy_m / (dy_m + dz_m)
            z_height = (1 - 2 * ver_mar - spacing) * dz_m / (dy_m + dz_m)
            width = height * dx_m / dy_m

        return width, height, z_height

    def calc_sizes_single(size_dict, hor_mar=0.05, ver_mar=0.05):
        dx_m = size_dict['dx']
        dy_m = size_dict['dy']

        if dx_m > dy_m:
            width = 1 - 2 * hor_mar
            height = width * dy_m / dx_m
        else:
            height = 1 - 2 * ver_mar
            width = height * dx_m / dy_m

        return width, height

    logger = logging.getLogger('sim_log')

    # Constants
    hor_mar = 0.05
    ver_mar = 0.05
    spacing = 0.05
    alpha_pt = 0.4

    size_dict = mesh_data['range']
    mesh_info = mesh_data['mesh_info']

    # Set figure
    width, height, z_height = calc_sizes(size_dict, spacing, hor_mar, ver_mar)

    xy_view = [hor_mar, ver_mar, width, height]
    xz_view = [hor_mar, ver_mar + height + spacing, width, z_height]
    yz_view = [hor_mar + width + spacing, ver_mar, z_height, height]

    fig = plt.figure(figsize=(9, 9))

    xy_view = plt.axes(xy_view)
    xy_view.tick_params(direction='in', top=True, right=True)
    xz_view = plt.axes(xz_view)
    xz_view.tick_params(direction='in', labelbottom=False)
    yz_view = plt.axes(yz_view)
    yz_view.tick_params(direction='in', labelleft=False)

    # Upload images
    img = mpimg.imread(os.path.join(output_loc, 'imgs', 'xy.png'))
    xy_view.imshow(img, zorder=0,
                   extent=[size_dict['xmin'], size_dict['xmax'],
                           size_dict['ymin'], size_dict['ymax']], cmap='gray')
    img = mpimg.imread(os.path.join(output_loc, 'imgs', 'xz.png'))
    xz_view.imshow(img, zorder=0,
                   extent=[size_dict['xmin'], size_dict['xmax'],
                           size_dict['zmin'], size_dict['zmax']], cmap='gray')
    img = Image.open(os.path.join(output_loc, 'imgs', 'yz.png')).transpose(Image.ROTATE_90).transpose(
        Image.FLIP_LEFT_RIGHT)
    yz_view.imshow(img, zorder=0,
                   extent=[size_dict['zmin'], size_dict['zmax'],
                           size_dict['ymin'], size_dict['ymax']], cmap='gray')

    # Upload points
    r = re.compile('^m\d+$')
    sorted_columns = list(filter(r.match, list(data.columns)))

    if data_type == 'vel_err':
        data['loc_extr'] = data['vel_err_loc']
        data['est'] = data['vel_err']
    elif data_type == 'press_err':
        data['loc_extr'] = data['press_err_loc']
        data['est'] = data['press_err']
    else:

        if which_mesh == 'max':
            data['est'] = data[sorted_columns].max(axis=1)
            data['mesh'] = data[sorted_columns].idxmax(axis=1)
        else:
            data['est'] = data[f'm{which_mesh}']
            data['mesh'] = f'm{which_mesh}'

        data['mesh'] = [''.join([x, '_loc']) for x in data['mesh']]
        data['loc_extr'] = data.lookup(data.index, data['mesh'])

    #Remove nan values
    if data['est'].isnull().any():
        logger.warning(f'NaN values in {data_type} data for location plot. Removing them before plotting.')
        data = data.dropna(subset=['est'])
        data = data.reset_index(drop=True)


    data['loc_extr'] = data['loc_extr'].apply(lambda x: x.strip("[]").replace("'", "").split(", "))
    coords = pd.DataFrame(data['loc_extr'].tolist(), columns=['x', 'y', 'z'])
    coords = coords.astype('float')

    xy_view.scatter(coords['x'], coords['y'], s=5, alpha=alpha_pt)
    xy_view.scatter(coords['x'][-last_points:], coords['y'][-last_points:],
                    s=5, alpha=0.8, color='orange', label=f'Last {last_points} pts.')
    xy_view.scatter(coords.loc[data['est'].idxmax(), 'x'],
                    coords.loc[data['est'].idxmax(), 'y'],
                    s=20, color='#D62728', marker='^', alpha=1, label=f'Max value')
    xy_view.legend()

    xz_view.scatter(coords['x'], coords['z'], s=5, alpha=alpha_pt)
    xz_view.scatter(coords['x'][-last_points:], coords['z'][-last_points:],
                    s=5, alpha=0.8, color='orange', label=f'Last {last_points} pts.')
    xz_view.scatter(coords.loc[data['est'].idxmax(), 'x'],
                    coords.loc[data['est'].idxmax(), 'z'],
                    s=20, color='#D62728', marker='^', alpha=1, label=f'Max value')

    yz_view.scatter(coords['z'], coords['y'], s=5, alpha=alpha_pt)
    yz_view.scatter(coords['z'][-last_points:], coords['y'][-last_points:],
                    s=5, alpha=0.8, color='orange', label=f'Last {last_points} pts.')
    yz_view.scatter(coords.loc[data['est'].idxmax(), 'z'],
                    coords.loc[data['est'].idxmax(), 'y'],
                    s=20, color='#D62728', marker='^', alpha=1, label=f'Max value')

    for k in mesh_info:
        mesh = mesh_info[k]
        rect_xy = patches.Rectangle((mesh[3], mesh[5]),
                                    mesh[4] - mesh[3], mesh[6] - mesh[5],
                                    linewidth=1, edgecolor='green', facecolor='none', alpha=0.5)

        rect_xz = patches.Rectangle((mesh[3], mesh[7]),
                                    mesh[4] - mesh[3], mesh[8] - mesh[7],
                                    linewidth=1, edgecolor='green', facecolor='none', alpha=0.5)

        rect_yz = patches.Rectangle((mesh[7], mesh[5]),
                                    mesh[8] - mesh[7], mesh[6] - mesh[5],
                                    linewidth=1, edgecolor='green', facecolor='none', alpha=0.5)

        xy_view.add_patch(rect_xy)
        xz_view.add_patch(rect_xz)
        yz_view.add_patch(rect_yz)

    titles = {'cfl': 'Max CFL',
              'min_div': 'Min Divergence',
              'max_div': 'Max Divergence',
              'vn': 'Max VN',
              'vel_err': 'Max Velocity Error',
              'press_err': 'Max Pressure Error'}

    if which_mesh == 'max':
        fig.suptitle(
            f'{titles[data_type]} Location\nLast Updated: {datetime.now().strftime("%d-%b-%Y %H:%M")}',
            fontsize=12, va='top')
    else:
        fig.suptitle(
            f'{titles[data_type]} Location for Mesh {which_mesh}\nLast Updated: {datetime.now().strftime("%d-%b-%Y %H:%M")}',
            fontsize=12, va='top')

    plt.savefig(os.path.join(output_loc, f'loc_{data_type}.png'), bbox_inches="tight")
    if show_debug:
        plt.show()
    plt.close(fig)

    if z_height > 5*width or z_height > 5*height:

        # w_single, h_single = calc_sizes_single(size_dict, hor_mar=0.1, ver_mar=0.1)
        # xy_view_s = [0.1, 0.1, w_single, h_single]

        fig, xy_view_s = plt.subplots()
        fig.set_size_inches(12, 7)
        # xy_view_s = plt.axes(xy_view_s)
        xy_view_s.tick_params(direction='in', top=True, right=True)
        img = mpimg.imread(os.path.join(output_loc, 'imgs', 'xy.png'))
        xy_view_s.imshow(img, zorder=0,
                       extent=[size_dict['xmin'], size_dict['xmax'],
                               size_dict['ymin'], size_dict['ymax']], cmap='gray')
        xy_view_s.scatter(coords['x'], coords['y'], s=12, alpha=0.4)
        xy_view_s.scatter(coords['x'][-last_points:], coords['y'][-last_points:],
                        s=12, alpha=0.8, color='orange', label=f'Last {last_points} pts.')
        xy_view_s.scatter(coords.loc[data['est'].idxmax(), 'x'],
                        coords.loc[data['est'].idxmax(), 'y'],
                        s=32, color='#D62728', marker='^', alpha=1, label=f'Max value')
        xy_view_s.legend()

        for k in mesh_info:
            mesh = mesh_info[k]
            rect_xy = patches.Rectangle((mesh[3], mesh[5]),
                                        mesh[4] - mesh[3], mesh[6] - mesh[5],
                                        linewidth=1, edgecolor='green', facecolor='none', alpha=0.5)
            xy_view_s.add_patch(rect_xy)

        if which_mesh == 'max':
            fig.suptitle(
                f'XY View {titles[data_type]} Location\nLast Updated: {datetime.now().strftime("%d-%b-%Y %H:%M")}',
                fontsize=12, va='top')
        else:
            fig.suptitle(
                f'XY View {titles[data_type]} Location for Mesh {which_mesh}\nLast Updated: {datetime.now().strftime("%d-%b-%Y %H:%M")}',
                fontsize=12, va='top')

        plt.savefig(os.path.join(output_loc, f'loc_xy_{data_type}.png'), bbox_inches="tight")
        plt.close(fig)