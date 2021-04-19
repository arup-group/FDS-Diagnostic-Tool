import matplotlib.pyplot as plt
import pandas as pd
import plot_fxn as plf
import seaborn as sns
import datetime
import os
import json
from matplotlib import gridspec

def mesh_plots(output_loc):

    data_loc = os.path.join(output_loc, 'data')

    sns.set()
    fig = plt.figure(figsize=(15,9))

    ax1 = plt.subplot(321)
    plf.cycle_stats_plot(data_loc, data_type='ts', subplot=True, ax=ax1)

    ax2 = plt.subplot(323)
    plf.mesh_stats_plot(data_loc, data_type='cfl', subplot=True, ax=ax2)

    ax3 = plt.subplot(322)
    plf.mesh_stats_plot(data_loc, data_type='min_div', subplot=True, ax=ax3)
    #
    ax4 = plt.subplot(324)
    plf.mesh_stats_plot(data_loc, data_type = 'max_div', subplot = True, ax = ax4)

    ax5 = plt.subplot(325)
    plf.derived_cpu_step_plot(data_loc, subplot=True, ax=ax5)

    ax6 = plt.subplot(326, sharex=ax1)
    plf.mesh_stats_plot(data_loc, data_type='vn', subplot=True, ax=ax6)

    fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}', fontsize=12, va='top')
    plt.tight_layout()
    plt.savefig(os.path.join(output_loc, 'mesh_plots.png'), bbox_inches = "tight")
    plt.show()

output_loc = r'C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r3'
sim_stat ='RUNNING'

data_loc = os.path.join(output_loc, 'data')
data = pd.read_csv(os.path.join(data_loc, 'cycle_info.csv'), parse_dates=['log_time'])
data = data.iloc[0:200]
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
with open(r"C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r3\data\sim_info.json") as f:
    sim_info = json.load(f)




sns.set()
fig = plt.figure(figsize=(15,9))
widths = [1,0.02, 1]
heights = [1, 0.01, 4]
spec = fig.add_gridspec(ncols=3, nrows=3, width_ratios=widths,
                          height_ratios=heights)

ax1 = fig.add_subplot(spec[0, :])
plf.timeprogress_bar_plot(data, sim_info, t_predict=mock_pred, subplot=True, ax=ax1)
ax2 = fig.add_subplot(spec[2, 0])
plf.log_interval_plot(data, subplot=True, ax=ax2)
ax3 = fig.add_subplot(spec[2, 2])
plf.comp_speed_plot(data, subplot=True, ax=ax3)

fig.suptitle(f'Sim Status: {sim_stat}\nLast Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}', fontsize=12, va='top')

plt.tight_layout()
plt.savefig(os.path.join(output_loc, 'time_progress.png'), bbox_inches="tight")
plt.show()

# plf.timestep_bar_plot(data_loc, 'cpu_tot')
# plf.hrr_plot(data_loc)
# plf.general_stats_plot(data_loc, 'm_error')
# plf.general_stats_plot(data_loc, 'press_itr')