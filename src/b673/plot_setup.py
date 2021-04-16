import matplotlib.pyplot as plt
import plot_fxn as plf
import seaborn as sns
import datetime

data_loc = r'C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r3\data'

sns.set()
fig = plt.figure(figsize=(15,9))


ax1 = plt.subplot(321)
plf.cycle_stats_plot(data_loc, data_type='ts', subplot=True, ax=ax1)

ax2 = plt.subplot(323, sharex=ax1)
plf.mesh_stats_plot(data_loc, data_type='cfl', subplot=True, ax=ax2)

ax3 = plt.subplot(322, sharex=ax1)
plf.mesh_stats_plot(data_loc, data_type='min_div', subplot=True, ax=ax3)
#
ax4 = plt.subplot(324, sharex=ax1)
plf.mesh_stats_plot(data_loc, data_type = 'max_div', subplot = True, ax = ax4)

ax5 = plt.subplot(325, sharex=ax1)
plf.derived_cpu_step_plot(data_loc, subplot=True, ax=ax5)

ax6 = plt.subplot(326, sharex=ax1)
plf.mesh_stats_plot(data_loc, data_type='vn', subplot=True, ax=ax6)

fig.suptitle(f'Last Updated: {datetime.datetime.now().strftime("%d-%b-%Y %H:%M")}', fontsize=12, va='top')
plt.tight_layout()
plt.savefig(r'C:\work\fds_tools\fds_diagnostics\tests\NTU_sc1_r3\test.png', bbox_inches = "tight")
plt.show()



# plf.timestep_bar_plot(data_loc, 'cpu_tot')
# plf.hrr_plot(data_loc)
# plf.general_stats_plot(data_loc, 'm_error')
# plf.general_stats_plot(data_loc, 'press_itr')