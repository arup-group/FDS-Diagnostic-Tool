import datetime

def process_models():

    """Main function for collating and passing the data from the developed models"""

    als_res = {}
    cur_time = datetime.datetime.now()

    als_res['current_datetime'] = cur_time.strftime("%d-%b-%Y %H:%M")


    return als_res