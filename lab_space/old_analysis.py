

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
