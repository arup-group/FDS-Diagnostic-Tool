import re
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import os
import json


def scrape_hrr_data(fds_f_path, hrr_curve_sampling_rate=1):
    """Scrapes relevant fire definition data from *.fds file"""

    # Paterns
    id_pattern = r"&SURF ID\s*=\s*'(.*?)'"
    hrrpua_pattern = r"HRRPUA\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)"
    ramp_pattern = r"RAMP_Q\s*=\s*'(.*?)'"
    surf_fyi_pattern = r"FYI\s*=\s*'(.*?)'"
    values_pattern = r"T\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)\s*,\s*F\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)"
    obst_pattern = r"XB\s*=\s*((?:(?:[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)[\s,]*?){6})"
    react_id_pattern = r"&REAC ID\s*=\s*'(.*?)'"
    react_other_patterns = {'FYI': r"FYI\s*=\s*'(.*?)'",
                            'soot_yield': r"SOOT_YIELD\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)",
                            'CO_yield': r"CO_YIELD\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)",
                            'C': r"C\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)",
                            'H': r"H\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)",
                            'O': r"O\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)",
                            'N': r"N\s*=\s*((?:[-+]?[0-9]*\.?[0-9]+)(?:[eE][-+]?[0-9]+)?)"}

    hrr_dict = {}
    hrr_curve = pd.DataFrame()
    design_fire = {}
    design_fire['area'] = 0
    design_fire['react'] = {}
    surf_centr = []

    outcome_surf = False
    outcome_react = False

    with open(fds_f_path, "r") as file:
        for line in file:
            result_id = re.search(id_pattern, line)

            if result_id is not None:
                outcome_surf = True
                id_name = result_id.group(1)
                hrr_dict[id_name] = {}

            if outcome_surf == True:
                result_hrrpua = re.search(hrrpua_pattern, line)
                if result_hrrpua is not None:
                    hrr_dict[id_name]['hrrpua'] = float(result_hrrpua.group(1))

                result_ramp = re.search(ramp_pattern, line)
                if result_ramp is not None:
                    hrr_dict[id_name]['ramp'] = result_ramp.group(1)

                result_surf_fyi = re.search(surf_fyi_pattern, line)
                if result_surf_fyi is not None:
                    hrr_dict[id_name]['fyi'] = result_surf_fyi.group(1)

                if re.search('\/$', line) is not None:
                    outcome_id = False

            react_id = re.search(react_id_pattern, line)

            if react_id is not None:
                outcome_react = True
                design_fire['react']['id'] = react_id.group(1)

            if outcome_react == True:
                for entry in react_other_patterns:
                    result = re.search(react_other_patterns[entry], line)
                    if result is not None:
                        if entry != 'FYI':
                            design_fire['react'][entry] = float(result.group(1))
                        else:
                            design_fire['react'][entry] = result.group(1)

                if re.search('\/$', line) is not None:
                    outcome_react = False

        hrr_dict = {k: v for k, v in hrr_dict.items() if v != {} and 'ramp' in v and 'hrrpua' in v}
        for entry in hrr_dict: hrr_dict[entry]['obst_area'] = []
        surfs_lst = [k for k in hrr_dict]
        ramp_id_lst = [hrr_dict[k]['ramp'] for k in hrr_dict]
        ramp_id_dict = {k: [] for k in ramp_id_lst}

        file.seek(0)
        for line in file:

            if '&RAMP' in line:
                # FIX this might break because of digits. FIXED longer string matches with priority
                match = [x for x in ramp_id_lst if x in line]
                if match != []:
                    value_dict = {}
                    value_result = re.search(values_pattern, line)
                    value_dict['T'] = float(value_result.group(1))
                    value_dict['F'] = float(value_result.group(2))
                    ramp_id_dict[max(match, key=len)].append(value_dict)

            if '&OBST' in line:
                # FIX this might break because of digits. FIXED longer string matches with priority
                match = [x for x in list(hrr_dict.keys()) if x in line]
                if match != []:
                    result = re.search(obst_pattern, line)
                    coords = [float(i) for i in re.split(',', result.group(1))]
                    area = (coords[1] - coords[0]) * (coords[3] - coords[2])
                    hrr_dict[match[-1]]['obst_area'].append(area) # gets the last match assuming obst defined with one fire surf
                    surf_centr.append(np.array([0.5 * (coords[1] + coords[0]), 0.5 * (coords[3] + coords[2])]))

    # Calculate total fire area and curve for each surface
    for entry in hrr_dict:
        hrr_dict[entry]['curv'] = pd.DataFrame(ramp_id_dict[hrr_dict[entry]['ramp']])
        surf_area = sum(hrr_dict[entry]['obst_area'])
        hrr_dict[entry]['curv']['Q_s'] = surf_area * hrr_dict[entry]['hrrpua'] * hrr_dict[entry]['curv']['F']
        design_fire['area'] = design_fire['area'] + surf_area

    # Calculate main fire curve
    max_time = max([hrr_dict[k]['curv']['T'].max() for k in hrr_dict.keys()])
    hrr_curve['t'] = np.arange(0, max_time, hrr_curve_sampling_rate)

    for entry in hrr_dict:
        f = interp1d(hrr_dict[entry]['curv']['T'], hrr_dict[entry]['curv']['Q_s'], fill_value='extrapolate')
        hrr_curve[entry] = f(hrr_curve['t'])
    hrr_curve['HRR'] = hrr_curve.drop('t', axis=1).sum(axis=1)
    hrr_curve['HRR'] = hrr_curve['HRR'].round(1)

    # Assemble final fire curve dictionary
    design_fire['max_HRR'] = round(hrr_curve['HRR'].max(), 0)
    design_fire['max_HRR_t'] = hrr_curve.loc[hrr_curve['HRR'].idxmax(), 't']
    design_fire['loc'] = np.mean(surf_centr, axis=0)
    design_fire['hrrpua'] = round(design_fire['max_HRR'] / design_fire['area'], 0)
    design_fire['area'] = round(design_fire['area'], 2)
    design_fire['curve'] = hrr_curve[['t', 'HRR']]
    design_fire['surf'] = hrr_dict

    return design_fire


def save_hrr_data(design_fire, save_loc):
    design_fire['curve'].to_csv(os.path.join(save_loc, 'data', 'hrr_curve.csv'), index=False)
    design_fire.pop('curve', None)
    design_fire['loc'] = design_fire['loc'].tolist()
    for i in design_fire['surf']:
        design_fire['surf'][i]['curv'] = design_fire['surf'][i]['curv'].to_dict(orient='records')
    with open(os.path.join(save_loc, 'data', 'hrr_data.json'), 'w') as fp:
        json.dump(design_fire, fp, indent=4)


def detect_growth_rate(design_fire):
    """Detect standard growth rate"""

    # treshold for autodetection of growth rate. Default set to 10% of CIBSE t2 predictions
    div_treshold = 0.1

    t2_data = pd.DataFrame.from_dict({'slow': [0.0029], 'medium': [0.0117], 'fast': [0.0469], 'ultrafast': [0.1876]},
                                     orient='index', columns=['alpha'])

    t2_data['hrr_est'] = t2_data['alpha'] * (design_fire['max_HRR_t']) ** 2
    t2_data['resd'] = t2_data['hrr_est'] - design_fire['max_HRR']

    if t2_data['resd'].abs().min() < div_treshold * design_fire['max_HRR']:
        design_fire['gr_rate'] = t2_data['resd'].abs().idxmin()
        design_fire['gr_resd'] = round(t2_data.loc[t2_data['resd'].abs().idxmin(), 'resd'], 1)
    else:
        design_fire['gr_rate'] = 'undef'
        design_fire['gr_resd'] = round(t2_data.loc[t2_data['resd'].abs().idxmin(), 'resd'], 1)

    return design_fire


def get_hrr_data(fds_f_path, save_loc, hrr_curve_sampling_rate=1):
    design_fire = scrape_hrr_data(fds_f_path, hrr_curve_sampling_rate)
    design_fire = detect_growth_rate(design_fire)
    save_hrr_data(design_fire, save_loc)