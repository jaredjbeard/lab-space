#!/usr/bin/env python3


from analysis import Analysis

if __name__ == "__main__":
    config = {
        "data_file" : "/home/jared/lab-space/lab_space/results/data.csv",
        "save_file" : "save.csv",
        "save_path" : "save/",
        "fig_params" : {},
        "cross_ref" : "letter",
        "x" : "longcount",
        "y" : "shortcount",
        "z" : None,
        "control" : None,
        "control_kwargs": 
        {
            "bins" : 
            { 
                "size": None,
                "bins": None # if a list, then the bins to use
            }    
        },
        "merge_cols":
        {
        #   "param": ["alpha", "c"]      
        },
        "filter" :
        {
            "rm_unused_cols" : False,
            # "logic" : 
            # {   "and":
            #     [
            #         {"col" : "letter", "op" : "in", "val" : "a"},
            #         # {"col" : "word", "op" : "nin", "val" : ["bee"]},
            #         {   "or":
            #             [
            #                 {"col" : "longcount", "op" : "in", "val" : [0,4]},
            #                 {"col" : "word", "op" : "in", "val" : ["bee"]},
            #             ]
            #         }
                
            #     ]
            # },
            "include_cols" : None,
            "exclude_cols" : []
        },
        "fig":
        {
            "type" : "line",
            "title" : "Test",
            "xlabel" : None,
            "ylabel" : "Short Count",
            "legend" : True,
            "legend_loc" : "upper left",
            "kwargs" : {},
            "controls":
            {   
                "smooth" : None, # number of els to smooth over
                "sort": 1, # 0 = no sort, 1 = sort, -1 =  reverse sort
                "avg": 1 # 0 = no avg, 1 = avg, 2 = median, 3 = mode
                
            }
        }
    }
    a = Analysis(config)
    a.analyze()