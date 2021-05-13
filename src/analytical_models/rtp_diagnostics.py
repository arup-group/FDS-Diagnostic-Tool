import rtp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


output_loc = r'C:\work\fds_tools\fds_diagnostics\tests\braehead_sc1_new'
mavg_window = 30
n_predictions = 7
pred_status = 'run'
n_trials = 300

# Setup logfile
log_record = []

# Setup a model
model = rtp.mAvg(output_loc, mavg_window, n_predictions, pred_status)

#Make a copy of the inital data
data_master = model.data.copy()

#Get prediction points for each trials
trials = [int(k) for k in np.linspace(mavg_window, len(data_master.index), n_trials)]

for k in trials:
    model.data = data_master.iloc[0:k].copy()
    model.check_status('run')
    model.predict()
    model.log(log_to_file=False, use_file=log_record)

log_record = pd.DataFrame(log_record)
plt.plot(log_record['sim_time'], log_record['T900_unc'].abs())
# plt.fill_between(log_record['sim_time'], (log_record['T900']-log_record['T900_unc']),
#                  (log_record['T900']+log_record['T900_unc']), color='b', alpha=.1)
# plt.plot(log_record['sim_time'], log_record['T300'])
# plt.plot(log_record['sim_time'], log_record['T450'])
# plt.plot(log_record['sim_time'], log_record['T600'])
# plt.plot(log_record['sim_time'], log_record['T750'])
# plt.plot(log_record['sim_time'], log_record['T150'])
plt.show()
print('asd')
