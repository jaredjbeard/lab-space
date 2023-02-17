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
        "logic_cols":
        {
            "name" : 
            [
                { "col" : <col_name>, "op" : <op>, "val" : <val>},
                { "col" : <col_name>, "op" : <op>, "val" : <val>}
            ]
        },
        "filter" :
        {
            "rm_unused_cols" : False,
            "include_vals" : 
            {
                "letter" : ["a", "b"]
            },
            "exclude_vals" :
            {
                "shortcount" : [1]
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