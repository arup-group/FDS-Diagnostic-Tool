import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from matplotlib.ticker import AutoMinorLocator


def day_rounder(date_min, type_round, h_intv):
    ''''Rounds axis times when timedate objects are used'''

    if type_round == 'd':
        if date_min.hour < 12:
            date_min = date_min.replace(second=0, microsecond=0, minute=0, hour=0)
        else:
            date_min = date_min.replace(second=0, microsecond=0, minute=0, hour=12)

        date_max = date_min + timedelta(hours=int(h_intv) + 6)

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
               '10000000': {'ML_fxn': mdates.DayLocator,
                            'itv': 4,
                            'mL': 4,
                            'fmt': '%d-%b',
                            'rnd': 'd',
                            'gr_sp': '1 d'}
               }

    for tdiff in [1, 6, 24, 96, 192, 288, 384, 10000000]:
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
    # Function starts here
    plot_type = {'vel_err': ['Velocity error (m/s)', 'Simulation time (s)'],
                 'press_err': ['Pressure error', 'Simulation time (s)']}


    data['est'] = data[data_type]
    data['mesh'] = data[f'{data_type}_m']

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


def timestep_bar_plot(data_loc, data_type):
    data = pd.read_csv(os.path.join(data_loc, data_type + '.csv'))
    r = re.compile('^m\d+$')
    sorted_columns = list(filter(r.match, list(data.columns)))

    performance = data[sorted_columns].max().sort_values()
    y_pos = np.arange(len(performance))
    objects = list(performance.index)

    fig, ax = plt.subplots(figsize=(15, 6))

    plt.barh(y_pos, performance, align='center', alpha=0.8)
    plt.yticks(y_pos, objects)
    plt.xlabel('Total time (s)')

    return performance


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
        fire_curve = pd.read_csv(os.path.join(data_loc, 'fire_curve.csv'))
        ax = plt.plot(fire_curve['t'], fire_curve['tot'], '--', color='red', label='HRR definition')
    except:
        pass

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


def comp_speed_plot(data, subplot=False, ax=None):

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

    plt.xlabel('Log time')
    plt.ylabel('Simulation speed (sph)')
    plt.xticks(rotation=30)
    plt.tight_layout()



    if subplot == False:
        plt.show()


def timeprogress_bar_plot(data, sim_info, t_predict = False, subplot=False, ax=None):

    date_start = datetime.strptime(sim_info["date_start"], "%B %d, %Y %H:%M:%S")

    if subplot == False:
        sns.set()
        fig, ax = plt.subplots(figsize=(15,2))

    # Plots
    ax.barh(1, data['sim_time'].max(), height=1, align='center', alpha=0.4)
    ax.barh(1, sim_info["sim_end"], height=1, edgecolor='#4C72B0', linewidth=1, fill=False, align='center')

    #Plot start
    ax.plot([1,1], [0.5, 1.5], color='#4C72B0', linewidth=4)
    ax.text(10,1, f'Start\n{date_start.strftime("%d-%b %H:%M")}', va='center')

    #Plot predictons
    if t_predict:
        for i in t_predict:
            if i['end']:
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed',  color='#DD8452', linewidth=2)
                ax.text(i['t']+9, 1, f'Complete\n{i["pr"]}\n($\pm${i["unc"]}h)', va='center', size=11)
            else:
                ax.plot([i['t'], i['t']], [0.5, 1.5],linestyle='dashed',  color='#DD8452', linewidth=2)
                ax.text(i['t']+9, 1, f'{i["pr"]}\n($\pm${i["unc"]}h)', va='center', size=11)




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

