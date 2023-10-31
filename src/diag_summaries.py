from collections import OrderedDict

class diagnosticsSummary():

    def __init__(self, input_entries):

        self.summary_timestamp = None
        self.sanitized_entries = {}
        self._sanitize_entries(input_entries)


    def _sanitize_entries(self, input_entries):
        """Sanitizes entries:
        1) Removes entries with critical error
        2) Puts them in ordered dictionary"""

        self.sanitized_entries = {i['cls_ID']: i for i in input_entries if i['diagnostic_error_count'][0] == 0}
        self.sanitized_entries = OrderedDict(sorted(self.sanitized_entries.items()))


    def _plot_summary_graph(self):

        # Allocate figure size
        # Allocate grid
        # Plot at each grid location
        pass



    def _save_summary_table(self):
        pass