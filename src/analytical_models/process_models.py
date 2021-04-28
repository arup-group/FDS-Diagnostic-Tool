import datetime
import analytical_models.status_prediction as status_prediction

def prm_main(output_loc):

    """Main function for collating and passing the data from the developed models"""

    als_res = {}
    als_res['cur_datetime'] = datetime.datetime.now()
    als_res['sim_status'] = status_prediction.status_prediction_main(output_loc, als_res['cur_datetime'])
    als_res['runtime_pred'] = [{'t': 400,
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
    return als_res
