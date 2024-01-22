from collections import OrderedDict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
import os
import json

class diagnosticsSummary():

    #TODO - create centralised control for diagnostics
    #TODO - average direction

    def __init__(self, input_entries, save_loc):

        self.summary_timestamp = datetime.datetime.now().strftime("%d-%b-%Y %H:%M")
        self.sanitized_entries = {}
        self.save_loc = save_loc
        self._sanitize_entries(input_entries)


    def _sanitize_entries(self, input_entries):
        """Sanitizes entries:
        1) Removes entries with critical error
        2) Puts them in ordered dictionary"""

        self.sanitized_entries = {i['cls_ID']: i for i in input_entries if i['diagnostic_error_count'][0] == 0}
        self.sanitized_entries = OrderedDict(sorted(self.sanitized_entries.items()))


    def _plot_summary_graph(self):

        #layout_parameters
        width_ratio = [1]
        height_ratio = [0.25, 0.5]
        grid_height_ratios = []

        # Allocate figure size
        sns.set()
        fig = plt.figure(constrained_layout=True, figsize=(14, 1.9 * len(self.sanitized_entries)))
        # fig = plt.figure(constrained_layout=True)
        [grid_height_ratios.extend(height_ratio) for _ in range(len(self.sanitized_entries))]
        spec = fig.add_gridspec(
            ncols=len(width_ratio),
            nrows=2*len(self.sanitized_entries),
            width_ratios=width_ratio,
            height_ratios=grid_height_ratios)

        for i, entry in enumerate(self.sanitized_entries):

            data = self.sanitized_entries[entry]

            ax_info = fig.add_subplot(spec[2*i, 0])
            diagnosticsSummary._display_status(data, ax=ax_info)
            diagnosticsSummary._display_progress(data, ax=ax_info)
            diagnosticsSummary._display_speed(data, ax=ax_info)
            ax_info.set_axis_off()

            ax_bar = fig.add_subplot(spec[2*i+1, 0])

            ax_bar.barh(1, data['sim_status']['lst_sim_time'], height=1, align='center', alpha=0.4)
            ax_bar.barh(1, data['sim_status']['end_sim_time'], height=1, edgecolor='#4C72B0', linewidth=1, fill=False,
                    align='center')
            ax_bar.set_xticks(np.linspace(0, data['sim_status']['end_sim_time'], 13))
            ax_bar.set_ylim([0.43, 1.57])
            ax_bar.set_xlim([0, 14/13*data['sim_status']['end_sim_time']])
            ax_bar.grid(b=True, which='major', linewidth=1.6)
            ax_bar.set_yticks([1])

            name = diagnosticsSummary._process_sim_name(data)
            ax_bar.set_yticklabels([name], ha='left', linespacing=1.3, size=11)
            ax_bar.yaxis.set_tick_params(pad=45)
            ax_bar.grid(axis='y')

            # ax_bar.text(0.1, 0.5, f'{entry} bar', transform=ax_bar.transAxes, va='center')
            ax_bar.set_xlabel('Simulation progress (s)', size=11)

            diagnosticsSummary._display_start_time(data, ax=ax_bar)
            diagnosticsSummary._display_last_time(data, ax=ax_bar)
            diagnosticsSummary._display_predictions(data, ax=ax_bar)

        fig.suptitle(f'FDS Diagnostic System 0.2.0\nLast Updated: {self.summary_timestamp}\n', fontsize=12, va='top',linespacing=1.4)
        plt.savefig(os.path.join(self.save_loc, "summary.png"), dpi=150)

    @staticmethod
    def _process_sim_name(data):
        """Processes label name"""

        # Check how many capitals are in the label
        if sum([i.isupper() for i in data['sim_name']]) < 2:
            if len(data['sim_name']) > 9:
                new_name = f"{data['sim_name'][:2]}..{data['sim_name'][-4:]}"
            else:
                new_name = data['sim_name']
        else:
            if len(data['sim_name']) > 6:
                new_name = f"{data['sim_name'][:2]}..{data['sim_name'][-3:]}"
            else:
                new_name = data['sim_name']

        return f"{data['cls_ID']}\n{new_name}\n{data['user_ID']}"

    @staticmethod
    def _display_status(data, ax):

        info = {
            'stopped': {'msg': 'Stopped', 'color': '#2CA02C'},
            'stalled': {'msg': 'Stalled', 'color': '#C44E52'},
            'completed': {'msg': 'Completed', 'color': '#2CA02C'},
            'instability': {'msg': 'Instability', 'color': '#C44E52'},
            'delayed': {'msg': 'Delayed', 'color': '#DD8452'},
            'running': {'msg': 'Running', 'color': '#2CA02C'}}

        status = data['sim_status']['status']
        ax.text(0, 0, info[status]['msg'],
                transform=ax.transAxes,
                ha='left',
                color=info[status]['color'],
                size=11,
                weight='demibold')

    @staticmethod
    def _display_progress(data, ax):
        progress = round(data['sim_status']['lst_sim_time'])
        ax.text(0.07, 0, f'{progress} s', transform=ax.transAxes, ha='left', size=11)

    @staticmethod
    def _display_speed(data, ax):

        if data['rtp']['model_status'] == 'no_run':
            speed = '--- s/h'
        elif data['sim_status']['status'] == 'completed':
            speed = '--- s/h'
        else:
            speed = f"{data['rtp']['avg_spd']} s/h"
        ax.text(0.115, 0,  speed, transform=ax.transAxes, ha='left', size=11)

    @staticmethod
    def _display_start_time(data, ax):

        start_date = datetime.datetime.strptime(data['sim_status']['sim_date_start'], "%d/%m/%Y %H:%M:%S")
        ax.text(0.01, 0.5, f'Started\n{start_date.strftime("%d/%m %H:%M")}',
                va='center',
                transform=ax.transAxes,
                size=10)

    @staticmethod
    def _display_last_time(data, ax):
        if data['sim_status']['status'] in ['running', 'delayed']:
            return

        lst_log_time = datetime.datetime.strptime(data['sim_status']['lst_log_time'], "%d/%m/%Y %H:%M:%S")

        if data['sim_status']['status'] == 'completed':
            print('here')
            ax.plot([data['sim_status']['lst_sim_time'], data['sim_status']['lst_sim_time']], [0.4, 1.5],
                linestyle='solid', color='#2CA02C', linewidth=2)
            ax.text(data['sim_status']['lst_sim_time'] + 0.008*data['sim_status']['end_sim_time'], 1,
                    f'Completed\n{lst_log_time.strftime("%d/%m %H:%M")}', va='center', size=10)

        elif data['sim_status']['status'] in ['stalled', 'instability']:
            ax.plot([data['sim_status']['lst_sim_time'], data['sim_status']['lst_sim_time']], [0.4, 1.5],
                    linestyle='solid', color='#C44E52', linewidth=2)
            ax.text(data['sim_status']['lst_sim_time'] + 0.008*data['sim_status']['end_sim_time'], 1,
            f'Last log\n{lst_log_time.strftime("%d/%m %H:%M")}', va='center', size=10)

    @staticmethod
    def _display_predictions(data, ax):

        if data['sim_status']['status'] not in ['running', 'delayed']:
            return

        if data['rtp']['model_status'] == 'no_data':
            ax.text(0.5*ax.get_xlim()[1], 1, 'Insufficient data\nfor accurate runtime prediction',
                    ha='center', va='center', size=10)
            return

        for i in data['rtp']['predicts']:
            pr_date = datetime.datetime.strptime(i['pr_date'], "%d/%m/%Y %H:%M:%S")
            pr_date = pr_date.strftime("%d/%m %H:%M")
            if i['pr_type'] == 'mid':
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed', color='#2CA02C', linewidth=2)
                ax.text(i['t'] + 0.008*data['sim_status']['end_sim_time'], 1, f'{pr_date}\n($\pm${i["unc"]}h)', va='center', size=10)
            elif i['pr_type'] == 'end':
                ax.plot([i['t'], i['t']], [0.5, 1.5], linestyle='dashed', color='#2CA02C', linewidth=2)
                ax.text(i['t'] + 0.008*data['sim_status']['end_sim_time'], 1, f'{pr_date}\n($\pm${i["unc"]}h)', va='center', size=10)

    def _save_summary_tabular(self):
        pass

    def _save_summary_json(self):
        with open(os.path.join(self.save_loc, "summary.json"), 'w', encoding='utf-8') as f:
            json.dump(self.sanitized_entries, f, ensure_ascii=False, indent=4)

    def process_summaries(self):
        self._plot_summary_graph()
        self._save_summary_tabular()
        self._save_summary_json()