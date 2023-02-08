import sys
import os

from numpy import var
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import json
import pickle

import re
import numpy as np
import random
import copy
import itertools


import matplotlib.pyplot as plt

## functions
def get_distance(s1, s2):
        return ((s1[0]-s2[0])**2 + (s1[1]-s2[1])**2)**0.5
    
def compute_min_time(d):
    return np.ceil(d/(2**(1/2)))

var_file = sys.argv[1]
print(var_file)
test_file = sys.argv[2]
print(test_file)
dep_variable = sys.argv[3]
print(dep_variable)
indep_variable = sys.argv[4]
print(indep_variable)
if indep_variable == "alpha":
    uct_indep = "c"
else:
    uct_indep = indep_variable
if len(sys.argv) > 5:
    crossref_variable = sys.argv[5]
    if crossref_variable == "alpha":
        uct_cr = "c"
    else:
        uct_cr = crossref_variable
else:
    crossref_variable = None
print(crossref_variable)
if len(sys.argv) > 6:
    print(sys.argv[6])
    data_filter = int(sys.argv[6])
else:
    data_filter = 0

f = open(current + "/../config/analysis/" + var_file +  ".json")
var_config = json.load(f)
f = open(current + "/../config/analysis/" + test_file +  ".json")
test_env = json.load(f)

if test_env["aogs_file"] != "":
    with open(current + "/../analysis/multithread/" + test_env["aogs_file"] , "rb") as f:
            aogs_pickle = pickle.load(f)
if test_env["gbop_file"] != "":
    with open(current + "/../analysis/multithread/" + test_env["gbop_file"] , "rb") as f:
            gbop_pickle = pickle.load(f)
if test_env["uct_file"] != "":
    with open(current + "/../analysis/multithread/" + test_env["uct_file"] , "rb") as f:
            uct_pickle = pickle.load(f)

aogs_data = []
gbop_data = []
uct_data = []
for d in aogs_pickle:
    params = re.split(r'_+', d)
    params.pop()
    
    if len(aogs_pickle[d]["R"]) != 0:
        temp = []
        for i in range(len(aogs_pickle[d]["R"])):
            temp_d = {}
            temp_d["epsilon"] = params[0]
            temp_d["delta"] = params[1]
            temp_d["horizon"] = params[2]
            temp_d["max_samples"] = params[3]
            temp_d["alpha"] = params[4]
            temp_d["probabilities"] = params[6]
            
            do_append = True
            for el in temp_d:
                if float(temp_d[el]) not in var_config[el]:
                    # print(el, temp_d[el], var_config[el], float(temp_d[el]) not in var_config[el] )
                    do_append = False
                # plt.pause(1)
                    
            temp_d["init"] = aogs_pickle[d]["init"][i]["pose"]
            temp_d["goal"] = aogs_pickle[d]["goal"][i]
            #print("aogs", temp_d["init"], temp_d["goal"])
            temp_d["r"] = aogs_pickle[d]["R"][i]
            temp_d["t"] = aogs_pickle[d]["ts"][i]
            # print(temp_d["init"],temp_d["goal"])
            temp_d["d"] = str(get_distance(temp_d["init"],temp_d["goal"]))
            # print(do_append, temp_d["alpha"])
            if do_append:
                temp.append(copy.deepcopy(temp_d))
        
        aogs_data = aogs_data + temp
# for el in aogs_data:
#     print(el)   
     
for d in gbop_pickle:
    params = re.split(r'_+', d)
    params.pop()
    
    if len(gbop_pickle[d]["R"]) != 0:
        temp = []
        for i in range(len(gbop_pickle[d]["R"])):
            temp_d = {}
            temp_d["epsilon"] = params[0]
            temp_d["delta"] = params[1]
            temp_d["horizon"] = params[2]
            temp_d["max_samples"] = params[3]
            temp_d["alpha"] = params[4]
            temp_d["probabilities"] = params[6]
            
            do_append = True
            for el in temp_d:
                if float(temp_d[el]) not in var_config[el]:
                    # print(el, temp_d[el], var_config[el], float(temp_d[el]) not in var_config[el] )
                    do_append = False
                    
            temp_d["init"] = gbop_pickle[d]["init"][i]["pose"]
            temp_d["goal"] = gbop_pickle[d]["goal"][i]
            temp_d["r"] = gbop_pickle[d]["R"][i]
            temp_d["t"] = gbop_pickle[d]["ts"][i]
            temp_d["d"] = str(get_distance(temp_d["init"],temp_d["goal"]))

            if do_append:
                temp.append(copy.deepcopy(temp_d))
                        
        gbop_data = gbop_data + temp
    

for d in uct_pickle:
    params = re.split(r'_+', d)
    params.pop()
    if len(uct_pickle[d]["R"]) != 0:
        temp = []
        for i in range(len(uct_pickle[d]["R"])):
            temp_d = {}
            temp_d["horizon"] = params[0]
            temp_d["max_samples"] = params[1]
            temp_d["c"] = params[2]
            temp_d["probabilities"] = params[4]
            
            do_append = True
            for el in temp_d:
                if float(temp_d[el]) not in var_config[el]:
                    # print(el, temp_d[el], var_config[el], float(temp_d[el]) not in var_config[el] )
                    do_append = False
                    
            temp_d["init"] = uct_pickle[d]["init"][i]["pose"]
            temp_d["goal"] = uct_pickle[d]["goal"][i]
            temp_d["r"] = uct_pickle[d]["R"][i]
            temp_d["t"] = uct_pickle[d]["ts"][i]
            temp_d["d"] = str(get_distance(temp_d["init"],temp_d["goal"]))
            
            if do_append:
                temp.append(copy.deepcopy(temp_d))
        
        uct_data = uct_data + temp

# for el in aogs_data: 
#     print(el)
var_config["d"] = []

for x in aogs_data:
    # print(x)
    # plt.pause(20)
    if x["d"] not in var_config["d"]:
        var_config["d"].append(x["d"])
for x in gbop_data:
    if x["d"] not in var_config["d"]:
        var_config["d"].append(x["d"])
for x in uct_data:
    if x["d"] not in var_config["d"]:
        var_config["d"].append(x["d"])

var_config["d"] = [float(el) for el in var_config["d"]]
var_config["d"].sort()
var_config["d"] = [str(el) for el in var_config["d"]]
# print(var_config["d"])


# print(var_config["d"])
# print(var_config["d"])

# var_config["d"] = list(range(min(var_config["d"]), max(var_config["d"]), (max(var_config["d"])-min(var_config["d"]))/100 ))
            
### Plot
x = var_config[indep_variable]
if indep_variable == "alpha":
    uct_x = var_config[uct_indep]
else:
    uct_x = x.copy()

if crossref_variable == None:
    num_plots = 1
else:
    num_plots = len(var_config[crossref_variable]) + 1

splt_len = [int(np.ceil(np.sqrt(num_plots))), int(np.floor(np.sqrt(num_plots)))]
if splt_len[0]*splt_len[1] < num_plots:
    splt_len = [int(np.ceil(np.sqrt(num_plots))), int(np.ceil(np.sqrt(num_plots)))]
fig, ax = plt.subplots(splt_len[0],splt_len[1],figsize=(7.5, 7.5 ))
# fig.title(dep_variable)

# print(ax)
# print(splt_len)
# print(num_plots)
if crossref_variable != None:
    trials = copy.deepcopy(var_config[crossref_variable])
    trials.append(copy.deepcopy(var_config[crossref_variable]))

for i in range(num_plots):
    
    data = {}
    for el in x:
        data[str(el)] = []
        
    aogs_temp = copy.deepcopy(data)
    gbop_temp = copy.deepcopy(data)
    uct_temp = {}
    data = {}
    for el in uct_x:
        uct_temp[str(el)] = []
    # print(uct_temp)
    
    if crossref_variable != None:
        if type(trials[i]) == list:
            filtered_vars = trials[i]
        else:
            filtered_vars = [trials[i]]

        for el in aogs_data:
            # print(el)
            # print(type(el[crossref_variable]), type(filtered_vars[0]),(el[crossref_variable] in filtered_vars))
            if float(el[crossref_variable]) in filtered_vars:
                # print(dep_variable)
                # print(el[dep_variable])
                aogs_temp[el[indep_variable]].append(el[dep_variable])
        for el in gbop_data:
            if float(el[crossref_variable]) in filtered_vars:
                gbop_temp[el[indep_variable]].append(el[dep_variable])
        for el in uct_data:
            # print("--------")
            # print(uct_temp)
            # print(el)
            # print(el[uct_indep])
            if indep_variable not in ["epsilon", "delta"] and el[uct_cr] in filtered_vars:
                uct_temp[el[uct_indep]].append(el[dep_variable])
    else:
        for el in aogs_data:
            # print("--------")
            # print(aogs_temp)
            # print(el)
            # print(el[indep_variable])
            aogs_temp[el[indep_variable]].append(el[dep_variable])
        for el in gbop_data:
            gbop_temp[el[indep_variable]].append(el[dep_variable])
        for el in uct_data:
            if indep_variable not in ["epsilon", "delta"]:
                uct_temp[el[uct_indep]].append(el[dep_variable])
                
    # print("------------")
    # print(crossref_variable)
    # for el in aogs_temp:
    #     print(el)

    aogs_y = []
    gbop_y = []
    uct_y = []

    # print("----", aogs_temp)
    
    for el in x:
        
        aogs_y.append(np.average(np.array(aogs_temp[str(el)])))
        # print("aogs", len(aogs_temp[str(el)]))
        gbop_y.append(np.average(np.array(gbop_temp[str(el)])))
        # print("gbop", len(gbop_temp[str(el)]))
    if indep_variable not in ["epsilon", "delta"]:
        for el in uct_x:
            # print("uct", len(uct_temp[str(el)]))
            uct_y.append(np.average(np.array(uct_temp[str(el)])))
    
    ind = np.argwhere( np.invert( np.isnan(aogs_y)) )
    ind = ind.flatten()
    
    aogs_x = [float(x[i]) for i in ind]
    aogs_y = [aogs_y[i] for i in ind]
    
    ind = np.argwhere( np.invert( np.isnan(gbop_y)) )
    ind = ind.flatten()

    gbop_x = [float(x[i]) for i in ind]
    gbop_y = [gbop_y[i] for i in ind]
    
    ind = np.argwhere( np.invert( np.isnan(uct_y)) )
    ind = ind.flatten()
    uct_x = [float(x[i]) for i in ind]
    uct_y = [uct_y[i] for i in ind]
    
    #Need to fix rolling average because it moves the x values too...
    if data_filter:
        if len(aogs_x):
            aogs_x = np.convolve (aogs_x, np.ones(data_filter)/data_filter)
            aogs_y = np.convolve (aogs_y, np.ones(data_filter)/data_filter)
        if len(gbop_x):
            gbop_x = np.convolve (gbop_x, np.ones(data_filter)/data_filter)
            gbop_y = np.convolve (gbop_y, np.ones(data_filter)/data_filter)
        if len(uct_x):
            uct_x = np.convolve (uct_x, np.ones(data_filter)/data_filter)
            uct_y = np.convolve (uct_y, np.ones(data_filter)/data_filter)
    
    if indep_variable == "d":
        print(gbop_x)
    # print(x)
    # print(aogs_y)
    if num_plots == 1:
        ax.plot(aogs_x,aogs_y)
        ax.plot(gbop_x,gbop_y)
        if indep_variable not in ["epsilon", "delta"]: 
            ax.plot(uct_x,uct_y) 
        
        ax.set_title(str(indep_variable + " vs " + dep_variable))
        ax.legend(["aogs", "gbop", "uct"])
    else:
        # print([int(np.floor(i/splt_len[0])), int(i % splt_len[0])])
        x_ind = int(i % splt_len[0])
        y_ind = int(np.floor(i/splt_len[0]))
        
        ax[x_ind, y_ind].plot(aogs_x,aogs_y)
        ax[x_ind, y_ind].plot(gbop_x,gbop_y) 
        if indep_variable not in ["epsilon", "delta"]: 
            ax[x_ind, y_ind].plot(uct_x,uct_y) 
        
        ax[x_ind, y_ind].set_title(crossref_variable + " " + str(trials[i]))
        ax[x_ind, y_ind].legend(["aogs", "gbop", "uct"])
        ax[x_ind, y_ind].set_xlabel(indep_variable)
        ax[x_ind, y_ind].set_ylabel(dep_variable)
  
    
# fig.tight_layout()  
fig.subplots_adjust(hspace=0.5, wspace=0.3)
# plt.show()
# while 1:
#     plt.pause(1)

if crossref_variable == None:
    crossref_variable = ""

fig.savefig(current + "/plots/" + var_file + "_" + test_file + "_" + indep_variable + "_vs_" + dep_variable + "_cr_" + crossref_variable + ".eps", format="eps", bbox_inches="tight", pad_inches=0)
fig.savefig(current + "/plots/" + var_file + "_" + test_file + "_" + indep_variable + "_vs_" + dep_variable + "_cr_" + crossref_variable + ".png", format="png", bbox_inches="tight", pad_inches=0.0)
