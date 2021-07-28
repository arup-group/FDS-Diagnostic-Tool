# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 17:41:22 2020

@author: javor
"""

import json
import pandas as pd
import numpy as np
from analysis_fxn import scrape_obst
import time
from PIL import Image
from PIL import ImageOps

def compute_size_z(data_filepath, fds_filepath, n):
    with open(data_filepath, 'r') as fp:
        data_dict = json.load(fp)
        
    sizes_lst = list()
    size_dict = {}
    
    
    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['z_min']  = mesh_list[7]
        size_dict['z_max']  = mesh_list[8]
        size_dict['A']  = round (((mesh_list[4] - mesh_list[3]) * (mesh_list[6] - mesh_list[5]))/(n**2),0)
        sizes_lst.append(size_dict)
        size_dict = {}
        
    sizes_pd = pd.DataFrame(sizes_lst)
    index_lst = np.round( np.arange(sizes_pd.z_min.min(), sizes_pd.z_max.max(), n), 1)
    domain_size_lst = []
    
    for k in index_lst:
         sorted_sizes = sizes_pd[(sizes_pd.z_max > k) & (sizes_pd.z_min <= k)]
         domain_size_lst.append(sorted_sizes.A.sum())
         
    domain_size_srs = pd.Series(domain_size_lst, index = index_lst, name = 'dom_size') 
    

    obst_pd = scrape_obst(fds_filepath, n)
    count_z = obst_pd.z.value_counts().sort_index()
    dom_size = pd.concat([count_z, domain_size_srs], axis = 1 )
    dom_size['ratio'] = dom_size.z / dom_size.dom_size
    
    return dom_size

def compute_size_uni(data_filepath, n):
    with open(data_filepath, 'r') as fp:
        data_dict = json.load(fp)
        
    sizes_lst = list()
    size_dict = {}
    
    
    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['z_min']  = mesh_list[7]
        size_dict['z_max']  = mesh_list[8]
        size_dict['y_min']  = mesh_list[5]
        size_dict['y_max']  = mesh_list[6]
        size_dict['x_min']  = mesh_list[3]
        size_dict['x_max']  = mesh_list[4]        
        size_dict['x_n']  = round ((mesh_list[4] - mesh_list[3])/n,0)
        size_dict['y_n']  = round ((mesh_list[6] - mesh_list[5])/n,0)
        sizes_lst.append(size_dict)
        size_dict = {}
        
    sizes_pd = pd.DataFrame(sizes_lst)
    index_side_lst = np.round( np.arange(sizes_pd.y_min.min(), sizes_pd.y_max.max(), n), 1)
    index_z_lst = np.round( np.arange(sizes_pd.z_min.min(), sizes_pd.z_max.max(), n), 1)
    
    domain_size_lst = []
    domain_size_pd = pd.DataFrame()
    domain_size_np = np.zeros([len(index_z_lst), len(index_side_lst)])
#    
#    for k in index_z_lst:
#       for j in index_side_lst:
#           sorted_sizes = sizes_pd[(sizes_pd.z_max > k) & (sizes_pd.z_min <= k) & (sizes_pd.y_max > j) & (sizes_pd.y_min <= j)]
#           domain_size_pd.loc[k, str(j)] = sorted_sizes['x_n'].sum()
# TODO count each mesh aeparately and update them
    
    for k, z_val in enumerate(index_z_lst):        
       sorted_sizes_z = sizes_pd[(sizes_pd.z_max > z_val) & (sizes_pd.z_min <= z_val)]
       for j, side_val in enumerate(index_side_lst):
           sorted_sizes = sorted_sizes_z[(sorted_sizes_z.y_max > side_val) & (sorted_sizes_z.y_min <= side_val)]
           domain_size_np[k,j] = sorted_sizes['x_n'].sum()
           
#    domain_size_srs = pd.Series(domain_size_lst, index = index_lst, name = 'dom_size') 
    
    return domain_size_np


def compute_size_uni_v2(data_filepath,fds_filepath,  n, vp):
    
    dirs = {'xz' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['z_min', 'z_max', 'z'], 'norm' : ['y_n']},
            'yz' : {'w' : ['y_min', 'y_max', 'y'],  'h' : ['z_min', 'z_max', 'z'], 'norm' : ['x_n']},
            'xy' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['y_min', 'y_max', 'y'], 'norm' : ['z_n']}}
    
    
    with open(data_filepath, 'r') as fp:
        data_dict = json.load(fp)
        
    sizes_lst = list()
    size_dict = {}
    
    
    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['z_min']  = mesh_list[7]
        size_dict['z_max']  = mesh_list[8]
        size_dict['y_min']  = mesh_list[5]
        size_dict['y_max']  = mesh_list[6]
        size_dict['x_min']  = mesh_list[3]
        size_dict['x_max']  = mesh_list[4]        
        size_dict['x_n']  = round ((mesh_list[4] - mesh_list[3])/n,0)
        size_dict['y_n']  = round ((mesh_list[6] - mesh_list[5])/n,0)
        size_dict['z_n'] = round((mesh_list[8] - mesh_list[7])/n,0)
        sizes_lst.append(size_dict)
        size_dict = {}
        
    sizes_pd = pd.DataFrame(sizes_lst)
    width_dict = {}
    height_dict = {}
    
    for k, j in  enumerate(np.round(np.arange(sizes_pd[dirs[vp]['w'][0]].min(), sizes_pd[dirs[vp]['w'][1]].max()+0.01, n), 1)):
        width_dict[str(j)] = k       
    for k, j in enumerate(np.round(np.arange(sizes_pd[dirs[vp]['h'][0]].min(), sizes_pd[dirs[vp]['h'][1]].max()+0.01, n), 1)):
        height_dict[str(j)] = k

    
    domain_size_np = np.zeros([len(height_dict), len(width_dict)])

# TODO count each mesh aeparately and update them
    
    for i in sizes_lst:
        w1 = width_dict[str(i[dirs[vp]['w'][0]])]
        w2 = width_dict[str(i[dirs[vp]['w'][1]])]
        h1 = height_dict[str(i[dirs[vp]['h'][0]])]
        h2 = height_dict[str(i[dirs[vp]['h'][1]])]
        
        domain_size_np[h1:(h2+1), w1:(w2+1)] += i[dirs[vp]['norm'][0]]
           
#    create obstruction array
    
    obst_dstr = np.zeros(np.shape(domain_size_np))
    obst_pd = scrape_obst(fds_filepath, n).round(1)
    obst_groups = obst_pd.groupby([dirs[vp]['h'][2]])
    
    for group in obst_groups.groups.keys():

        obst_set = obst_groups.get_group(group)[dirs[vp]['w'][2]].value_counts().sort_index()
        obst_set_consc = np.arange(0, n*len(obst_set), n)        
        list_obst_sets = [d for _, d in obst_set.groupby((obst_set.index.values - obst_set_consc).round(1))]
        for obst in list_obst_sets:
#            print(len(obst))
#            print(obst.index)

            h = height_dict[str(group)]
            w1 = width_dict[str(obst.index[0])]
            w2 = width_dict[str(obst.index[-1])]
#            print(w1, w2)
            obst_dstr[h, w1:(w2+1)] += obst
        
    img = np.divide(obst_dstr, domain_size_np, out=np.zeros_like(obst_dstr), where=domain_size_np!=0)
    img = 255 - img*255
    img = Image.fromarray(img.astype(np.uint8))
    
    return img



def fingerprint_single(data_filepath,fds_filepath,  n, vp):
    
    dirs = {'xz' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['z_min', 'z_max', 'z'], 'norm' : ['y_n']},
            'yz' : {'w' : ['y_min', 'y_max', 'y'],  'h' : ['z_min', 'z_max', 'z'], 'norm' : ['x_n']},
            'xy' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['y_min', 'y_max', 'y'], 'norm' : ['z_n']}}
    
    
    with open(data_filepath, 'r') as fp:
        data_dict = json.load(fp)
        
    sizes_lst = list()
    size_dict = {}
    
    
    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['z_min']  = mesh_list[7]
        size_dict['z_max']  = mesh_list[8]
        size_dict['y_min']  = mesh_list[5]
        size_dict['y_max']  = mesh_list[6]
        size_dict['x_min']  = mesh_list[3]
        size_dict['x_max']  = mesh_list[4]        
        size_dict['x_n']  = round ((mesh_list[4] - mesh_list[3])/n,0)
        size_dict['y_n']  = round ((mesh_list[6] - mesh_list[5])/n,0)
        size_dict['z_n'] = round((mesh_list[8] - mesh_list[7])/n,0)
        sizes_lst.append(size_dict)
        size_dict = {}
        
    sizes_pd = pd.DataFrame(sizes_lst)
    width_dict = {}
    height_dict = {}
    
    for k, j in  enumerate(np.round(np.arange(sizes_pd[dirs[vp]['w'][0]].min(), sizes_pd[dirs[vp]['w'][1]].max()+0.01, n), 1)):
        name = str(j)
        if name == '-0.0': name = '0.0'
        width_dict[name] = k       
    for k, j in enumerate(np.round(np.arange(sizes_pd[dirs[vp]['h'][0]].min(), sizes_pd[dirs[vp]['h'][1]].max()+0.01, n), 1)):
        name = str(j)
        if name == '-0.0': name = '0.0'
        height_dict[str(j)] = k


    domain_size_np = np.zeros([len(height_dict), len(width_dict)])

# TODO count each mesh aeparately and update them
    
    for i in sizes_lst:
        w1 = width_dict[str(i[dirs[vp]['w'][0]])]
        w2 = width_dict[str(i[dirs[vp]['w'][1]])]
        h1 = height_dict[str(i[dirs[vp]['h'][0]])]
        h2 = height_dict[str(i[dirs[vp]['h'][1]])]
        
        #CHECK EDGES to avoid dou
        domain_size_np[h1:(h2+1), w1:(w2+1)] += i[dirs[vp]['norm'][0]]
           
#    create obstruction array
    
    obst_dstr = np.zeros(np.shape(domain_size_np))
    obst_pd = scrape_obst(fds_filepath, n).round(1)
    obst_groups = obst_pd.groupby([dirs[vp]['h'][2]])
#    print(obst_groups.groups.keys())
    
    for group in obst_groups.groups.keys():

        obst_set = obst_groups.get_group(group)[dirs[vp]['w'][2]].value_counts().sort_index()
        obst_set = obst_set.reset_index()   
        list_obst_sets = np.split(obst_set, np.flatnonzero(np.diff(obst_set['index']).round(1) != n) + 1)
        for obst in list_obst_sets:
#            print(len(obst))
#            print(obst.index)

            h = height_dict[str(group)]
            w1 = width_dict[str(obst['index'].iloc[0])]
            w2 = width_dict[str(obst['index'].iloc[-1])]
#            print(w1, w2)
            obst_dstr[h, w1:(w2+1)] += obst[dirs[vp]['w'][2]]
        
    img = np.divide(obst_dstr, domain_size_np, out=np.zeros_like(obst_dstr), where=domain_size_np!=0)
    img = 255 - img*255
    img = Image.fromarray(img.astype(np.uint8))
    
    return ImageOps.flip(img)


def fingerprint_3d(data_filepath,fds_filepath,  n):
    
    dirs = {'xz' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['z_min', 'z_max', 'z'], 'norm' : ['y_n']},
            'yz' : {'w' : ['z_min', 'z_max', 'z'],  'h' : ['y_min', 'y_max', 'y'], 'norm' : ['x_n']},
            'xy' : {'w' : ['x_min', 'x_max', 'x'],  'h' : ['y_min', 'y_max', 'y'], 'norm' : ['z_n']}}
    
    viewports = ['xz', 'yz', 'xy']
    
    
    with open(data_filepath, 'r') as fp:
        data_dict = json.load(fp)
        
    sizes_lst = list()
    size_dict = {} 
    
    obst_pd = scrape_obst(fds_filepath, n).round(1)
    
    for mesh in data_dict['mesh_info']:
        mesh_list = data_dict['mesh_info'][mesh]
        size_dict['name'] = mesh
        size_dict['z_min']  = mesh_list[7]
        size_dict['z_max']  = mesh_list[8]
        size_dict['y_min']  = mesh_list[5]
        size_dict['y_max']  = mesh_list[6]
        size_dict['x_min']  = mesh_list[3]
        size_dict['x_max']  = mesh_list[4]        
        size_dict['x_n']  = round ((mesh_list[4] - mesh_list[3])/n,0)
        size_dict['y_n']  = round ((mesh_list[6] - mesh_list[5])/n,0)
        size_dict['z_n'] = round((mesh_list[8] - mesh_list[7])/n,0)
        sizes_lst.append(size_dict)
        size_dict = {}
        
    sizes_pd = pd.DataFrame(sizes_lst)
    images = {}

    
    for vp in viewports:
        width_dict = {}
        height_dict = {}
    
        for k, j in  enumerate(np.round(np.arange(sizes_pd[dirs[vp]['w'][0]].min(), sizes_pd[dirs[vp]['w'][1]].max()+0.01, n), 1)):
            name = str(j)
            if name == '-0.0': name = '0.0'
            width_dict[name] = k       
        for k, j in enumerate(np.round(np.arange(sizes_pd[dirs[vp]['h'][0]].min(), sizes_pd[dirs[vp]['h'][1]].max()+0.01, n), 1)):
            name = str(j)
            if name == '-0.0': name = '0.0'
            height_dict[name] = k
        
        domain_size_np = np.zeros([len(height_dict), len(width_dict)])
           
        for i in sizes_lst:
            w1 = width_dict[str(i[dirs[vp]['w'][0]])]
            w2 = width_dict[str(i[dirs[vp]['w'][1]])]
            h1 = height_dict[str(i[dirs[vp]['h'][0]])]
            h2 = height_dict[str(i[dirs[vp]['h'][1]])]           
            #CHECK EDGES to avoid dou
            domain_size_np[h1:(h2+1), w1:(w2+1)] += i[dirs[vp]['norm'][0]]
                       
        obst_dstr = np.zeros(np.shape(domain_size_np))
        
        obst_groups = obst_pd.groupby([dirs[vp]['h'][2]])
        
        for group in obst_groups.groups.keys():   
            obst_set = obst_groups.get_group(group)[dirs[vp]['w'][2]].value_counts().sort_index()
            obst_set = obst_set.reset_index()   
            list_obst_sets = np.split(obst_set, np.flatnonzero(np.diff(obst_set['index']).round(1) != n) + 1)
            
            for obst in list_obst_sets:
                h = height_dict[str(group)]
                w1 = width_dict[str(obst['index'].iloc[0])]
                w2 = width_dict[str(obst['index'].iloc[-1])]
                obst_dstr[h, w1:(w2+1)] += obst[dirs[vp]['w'][2]]
            
        img = np.divide(obst_dstr, domain_size_np, out=np.zeros_like(obst_dstr), where=domain_size_np!=0)
        images[vp] = 255 - img*255
        
    h_max = max(images['xz'].shape[0], images['yz'].shape[0],images['xy'].shape[0])
    y_max = max(images['xz'].shape[1], images['yz'].shape[1],images['xy'].shape[1])
    img_pad = {}

        
    for vp in viewports:
        padding = np.full((h_max, y_max), 255)
        padding[0:0+images[vp].shape[0], 0:0+images[vp].shape[1]] = images[vp]
        img_pad[vp] = padding
        
    rgb = np.dstack((img_pad['xy'],img_pad['xz'],img_pad['yz'])).astype(np.uint8)
    img_rgb = Image.fromarray(rgb)


    return  ImageOps.flip(img_rgb)

start_time = time.time()
data_filepath = r'C:\work\fds_diagnostics\src\outputs\paisley\data.json'
fds_filepath = r'C:\work\fds_diagnostics\docs\paisley\Fire_Scenario_4_VentOption1.fds'
#vp = 'xy'
n = 0.2

#domain_size_srs = compute_size_z(data_filepath, n)
#obst_pd = scrape_obst(fds_filepath, n)
#count_z = obst_pd.z.value_counts().sort_index()
#dom_size = pd.concat([count_z, domain_size_srs], axis = 1 )
#dom_size['ratio'] = dom_size.z / dom_size.dom_size

b_np = compute_size_uni(data_filepath, n)
#test_xy_new = fingerprint_single(data_filepath, fds_filepath, n, vp)

#img_xy = fingerprint_single(data_filepath,fds_filepath,  n, 'xy')
#print (time.time()- start_time)
#img_yz = fingerprint_single(data_filepath,fds_filepath,  n, 'yz')
#print (time.time()- start_time)
#img_xz = fingerprint_single(data_filepath,fds_filepath,  n, 'xz')
#print (time.time()- start_time)
#img_4d = fingerprint_3d(data_filepath,fds_filepath,  n)
#print (time.time()- start_time)

#paisley = compute_size_z(data_filepath, fds_filepath, n)



