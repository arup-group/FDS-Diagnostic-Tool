import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
import seaborn as sns


def mesh_stats_plot(data_loc, data_type, subplot=False, ax=None):
    # Function starts here
    plot_type = {'min_div': ['Min divergence', 'Simulation time (s)'],
                 'max_div': ['Max divergence', 'Simulation time (s)'],
                 'cfl': ['CFL number', 'Simulation time (s)'],
                 'vn': ['VN number', 'Simulation time (s)'],
                 'cpu_step': ['Max time per timestep (s)', 'Simulation time (s)']}

    data = pd.read_csv(os.path.join(data_loc, data_type + '.csv'))
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


def general_stats_plot(data_loc, data_type, subplot=False, ax=None):
    # Function starts here
    plot_type = {'ts': ['Time step (s)', 'Simulation time (s)'],
                 'vel_err': ['Mesh vel. error', 'Simulation time (s)'],
                 'press_itr': ['Pressure', 'Simulation time (s)']}

    data = pd.read_csv(os.path.join(data_loc, 'cycle_info.csv'))

    if subplot == False:
        fig, ax = plt.subplots(figsize=(15, 6))
        sns.set()

    colors = sns.color_palette()
    ax = plt.plot(data['sim_time'], data[data_type], '-', color=colors[0], label= data_type)
    ax = plt.xlabel(plot_type[data_type][1])
    ax = plt.ylabel(plot_type[data_type][0])
    ax = plt.legend(loc=4)
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


def hrr_plot(data_loc):
    data = pd.read_csv(os.path.join(data_loc, 'hrr.csv'))

    r = re.compile('^m\d+$')

    sorted_columns = list(filter(r.match, list(data.columns)))
    data['est'] = data[sorted_columns].sum(axis=1)

    fig, ax = plt.subplots(figsize=(15, 6))
    sns.set()
    colors = sns.color_palette()
    ax = plt.plot(data['sim_time'], data['est'], '-', color=colors[0], label='HRR output')
    try:
        fire_curve = pd.read_csv(os.path.join(data_loc, 'fire_curve.csv'))
        ax = plt.plot(fire_curve['t'], fire_curve['tot'], '--', color='red', label='HRR definition')
    except:
        pass

    ax = plt.ylabel('Total HRR (KW)')
    ax = plt.xlabel('Simulation time (s)')
    ax = plt.legend()