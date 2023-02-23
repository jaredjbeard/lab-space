#!/usr/bin/env python
"""
This script is handle command line argmuents for starting analyzing data.
"""
__license__ = "BSD-3"
__docformat__ = 'reStructuredText'
__author__ = "Jared Beard"

from importlib.resources import path
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from copy import deepcopy
import argparse
import json
import reconfigurator.reconfigurator as rc
from reconfigurator.compiler import compile_as_generator, compile_to_list

from analysis import Analysis
from file_utils import merge_files


CORE_FILE_NAME = "/config/core/core.json"
CORE_DEFAULT_FILE_NAME = "/config/core/core_default.json"

# cross ref and control should bin if there are too many.
# Support a list of data files 

# MARKUP
# Should support aliasing so we can compare variables of similar function
# Should support binning of a variable either through number of bins or user specified bins.


    

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Lab Space Analysis CLI')
    parser.add_argument('-r',   '--run',           action="store_const", const=True,  help='Runs analysis, if unspecified runs user default')
    parser.add_argument('-ra',  '--run_all',       action="store_const", const=True,  help='Runs all analysis in path')
    
    parser.add_argument('-cr',  '--configure_reset', action="store_const", const=True, help='Resets all configuration to factory default')
    parser.add_argument('-cp',  '--configure_path',                 type=str, nargs=  1, help='Configures path of config and data files')
    parser.add_argument('-cdp', '--configure_data_path',            type=str, nargs=  1, help='Configures path of data files')
    parser.add_argument('-cdf', '--configure_data_file',            type=str, nargs=  1, help='Configures file name for saved data')
    parser.add_argument('-cap', '--configure_analysis_path',        type=str, nargs=  1, help='Configures path of analysis data files')
    parser.add_argument('-caf', '--configure_analysis_file',        type=str, nargs=  1, help='Configures file name for analysis data')
    parser.add_argument('-cfp', '--configure_figure_path',          type=str, nargs=  1, help='Configures path of figure files')
    parser.add_argument('-cff', '--configure_figure_file',          type=str, nargs=  1, help='Configures file name for figures')
    
    parser.add_argument('-aft',  '--figure_type',                   type=str, nargs=  1, help='Specifies the type of figure to plot')
    parser.add_argument('-afn',  '--figure_name',                   type=str, nargs=  1, help='Specifies the name of the figure')
    parser.add_argument('-acrv', '--cross_ref_variable',            type=str, nargs="+", help='Specifies the cross reference variable (the variable defining the legend). Can optionally add number of bins if too many values')
    parser.add_argument('-aiv',  '--independent_variable',          type=str, nargs=  1, help='Specifies the independent variable')
    parser.add_argument('-adv',  '--dependent_variable',            type=str, nargs=  1, help='Specifies the dependent variable')
    parser.add_argument('-azv',  '--z_variable',                    type=str, nargs=  1, help='Specifies the z variable')
    parser.add_argument('-acv',  '--control_variable',              type=str, nargs="+", help='Specifies the cross reference variable: generates subplots for each value of the control and all together. Can optionally add number of bins if too many values')
    parser.add_argument('-al',   '--log_level',                     type=str, nargs=  1, help='Sets log level')
    parser.add_argument('-ar',   '--render',           action="store_const", const=True, help='Renders figures')
    
    parser.add_argument('-m',    '--merge',                         type=str, nargs="+", help='Merges data from a list of files into a single file, uses the last file name as the save file name')

    parser.add_argument('-s',    '--save',            action="store_const", const=True,  help='Saves settings for experiment and trial data to current files. If trial is compiled, will append "c_" to file name and save compiled version')
    parser.add_argument('-sa',   '--save_analysis',                 type=str, nargs="+", help='Saves analysis data, if argument specified saves to that file in path')

    parser.add_argument('-p',    '--print',           action="store_const", const=True,  help='Prints config file')

    args = parser.parse_args()
    #########################################################################################
    # Configurations ------------------------------------------------------------------------
    with open(current + CORE_FILE_NAME, "rb") as f:
        core_config = json.load(f)
    with open(current + CORE_DEFAULT_FILE_NAME, "rb") as f:
        core_default = json.load(f)

    if args.configure_reset is not None:
        with open(current + CORE_FILE_NAME, "w") as f:
            json.dump(core_default, f, indent=4)
        print("Core Reset")
    
    if args.merge is not None:
        merge_files(args.merge)

    # #---> ##========>>
    if args.configure_path is not None:
        core_config["data_path"] = args.configure_path[0]
        core_config["analysis_path"] = args.configure_path[0]
        core_config["figure_path"] = args.configure_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)

    if args.configure_data_path is not None:
        core_config["data_path"] = args.configure_data_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.configure_data_file is not None:
        core_config["data_file"] = args.configure_data_file[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    
    if args.configure_analysis_path is not None:
        core_config["analysis_path"] = args.configure_analysis_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.configure_analysis_file is not None:
        core_config["analysis_file"] = args.configure_analysis_file[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.run_all is not None and not args.run_all:
        analysis_config = rc.read_file(core_config["analysis_path"] + core_config["analysis_file"])
    else:
        analysis_config = {}
        
    if args.configure_figure_path is not None:
        core_config["figure_path"] = args.configure_figure_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.configure_figure_file is not None:
        core_config["figure_file"] = args.configure_figure_file[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)    
        


    # Analysis Configurations ---------------------------------------------------------------
    
    if args.figure_type is not None:
        analysis_config["fig"]["type"] = args.figure_type[0]
    if args.figure_name is not None:
        analysis_config["fig"]["title"] = args.figure_name[0]
    if args.cross_ref_variable is not None:
        analysis_config["cross_ref"] = args.cross_ref_variable[0]
    if args.independent_variable is not None:
        analysis_config["x"] = args.independent_variable[0]
    if args.dependent_variable is not None:
        analysis_config["y"] = args.dependent_variable[0]
    if args.z_variable is not None:
        analysis_config["z"] = args.z_variable[0]
    if args.control_variable is not None:
        analysis_config["control"] = args.control_variable[0]
    if args.log_level is not None:
        analysis_config["log_level"] = args.log_level[0]
    elif "log_level" not in analysis_config:
        analysis_config["log_level"] = "WARNING"
    if args.render is not None and args.render:
        analysis_config["render"] = True
        
    # Save --------------------------------------------------------------------------------------------
    if args.save is not None and args.save:
        rc.write_file(core_config["expt_path"] + core_config["expt_name"], analysis_config)
    if args.save_analysis is not None and args.save_analysis:
        rc.write_file(core_config["expt_path"] + core_config["expt_name"], analysis_config)
    
    # # Print --------------------------------------------------------------------------------------------
    if args.print is not None and args.print:
        print(f'{"Core Config":-<20}')
        rc.print_config(core_config)
        print()
        print()
        print(f'{"Analysis Config":-<20}')
        rc.print_config(analysis_config)

    # Run --------------------------------------------------------------------------------------------
    if args.run_all is not None and args.run_all:
        file_names = os.listdir(core_config["analysis_path"])
        for name in file_names:
            if name.endswith(".json"):
                analysis_config = rc.read_file(core_config["analysis_path"] + name)
                analysis_config["data_file"] = analysis_config["data_path"] + analysis_config["data_file"]
                analysis_config["figure_file"] = analysis_config["figure_path"] + analysis_config["figure_file"]
                print(analysis_config["data_file"])
                if args.render is not None and args.render:
                    analysis_config["render"] = True
                analysis = Analysis(analysis_config, analysis_config["log_level"])
                analysis.run()
                
    if args.run is not None and args.run:
        analysis_config["data_file"] = analysis_config["data_path"] + analysis_config["data_file"]
        analysis_config["figure_file"] = analysis_config["figure_path"] + analysis_config["figure_file"]
        print(analysis_config["data_file"])
        analysis = Analysis(analysis_config, analysis_config["log_level"])
        analysis.run()