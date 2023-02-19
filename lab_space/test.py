#!/usr/bin/env python3


from analysis import Analysis

if __name__ == "__main__":
    config = {
        "data_file" : "/home/jared/lab-space/lab_space/results/data.csv",
        "save_file" : "save.csv",
        "save_path" : "save/",
        "type" : "line",
        "fig_params" : {},
        "cross_ref" : "letter",
        "ind_var" : "longcount",
        "dep_var" : "shortcount",
        "control_var" : None,
        "merge_cols":
        {
          "param": ["alpha", "c"]      
        },
        "filter" :
        {
            "rm_unused_cols" : False,
            "logic" : 
            {   
                "and":
                [
                    {"col" : "letter", "op" : "in", "val" : "a"},
                    # {"col" : "word", "op" : "nin", "val" : ["bee"]},
                    {
                        "or":
                        [
                            {"col" : "longcount", "op" : "in", "val" : [0,4]},
                            {"col" : "word", "op" : "in", "val" : ["bee"]},
                        ]
                    }
                
                ]
            },
            "include_cols" : None,
            "exclude_cols" : []
        },
        "fig":
        {
            "title" : "Test",
            "xlabel" : "Long Count",
            "ylabel" : "Short Count",
            "legend" : True,
            "legend_loc" : "upper left",
        }
    }
    a = Analysis(config)
    a.analyze()