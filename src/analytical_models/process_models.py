import datetime
import analytical_models.status_prediction as status_prediction
import analytical_models.rtp as rtp

def run_analytics(output_loc):

    """Main function for collating and passing the data from the developed models"""

    als_res = {}

    als_res['cur_datetime'] = datetime.datetime.now()

    #Simulation status model
    als_res['sim_status'] = status_prediction.status_prediction_main(output_loc, als_res['cur_datetime'])

    #Runtime prediction model:
    model = rtp.mAvg(output_loc, mavg_window=30, n_predictions=7, pred_status=als_res['sim_status']['stat'])
    model.predict()
    als_res['runtime_pred'] = model.report()


    return als_res
