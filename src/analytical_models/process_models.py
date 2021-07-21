import datetime
import logging
import analytical_models.status_prediction as status_prediction
import analytical_models.rtp as rtp

def run_analytics(output_loc):

    """Main function for collating and passing the data from the developed models"""
    logger = logging.getLogger('sim_log')

    als_res = {}

    als_res['cur_datetime'] = datetime.datetime.now()

    #Simulation status model
    try:
        als_res['sim_status'] = status_prediction.status_prediction_main(output_loc, als_res['cur_datetime'])
    except:
        als_res['sim_status'] = None
        logger.warning('Error in status prediction', exc_info=True)

    #Runtime prediction model:
    try:
        model = rtp.mAvg(output_loc, mavg_window=30, n_predictions=7, pred_status=als_res['sim_status']['stat'])
        model.predict()
        als_res['runtime_pred'] = model.report()
        logger.info(f'Runtime predicted with {model.model_name}.')
    except:
        als_res['runtime_pred'] = None
        logger.warning('Error in runtime prediction', exc_info=True)

    return als_res
