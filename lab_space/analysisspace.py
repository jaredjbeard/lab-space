#!/usr/bin/python3
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

from lab_space.old_analysis import Analysis

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
    
    parser.add_argument('-cr',  '--configure_reset', action="store_const", const=True, help='Resets all configuration to factory default')
    parser.add_argument('-cp',  '--configure_path',                 type=str, nargs=1, help='Configures path of config and data files')
    parser.add_argument('-csp', '--configure_save_path',            type=str, nargs=1, help='Configures path of save files')
    parser.add_argument('-csf', '--configure_save_file',            type=str, nargs=1, help='Configures file name for saved data')
    parser.add_argument('-cap', '--configure_analysis_path',        type=str, nargs=1, help='Configures path of analysis data files')
    parser.add_argument('-caf', '--configure_analysis_file',        type=str, nargs=1, help='Configures file name for analysis data')
    parser.add_argument('-cfp', '--configure_figures_path',         type=str, nargs=1, help='Configures path of figure files')

    parser.add_argument('-aff',  '--configure_figures_file',        type=str, nargs=1, help='Configures file name for figures')
    parser.add_argument('-aft',  '--figure_type',                   type=str, nargs=1, help='Specifies the type of figure to plot')
    parser.add_argument('-acrv', '--cross_ref_variable',            type=str, nargs="+", help='Specifies the cross reference variable (the variable defining the legend). Can optionally add number of bins if too many values')
    parser.add_argument('-aiv',  '--independent_variable',          type=str, nargs=1, help='Specifies the independent variable')
    parser.add_argument('-adv',  '--dependent_variable',            type=str, nargs=1, help='Specifies the dependent variable')
    parser.add_argument('-acv',  '--control_variable',              type=str, nargs="+", help='Specifies the cross reference variable: generates subplots for each value of the control and all together. Can optionally add number of bins if too many values')
    parser.add_argument('-al',  '--log_level',                      type=str, nargs = 1,  help='Sets log level')

    parser.add_argument('-ac',  '--compile',           action="store_const", const=True,  help='Compiles analysis config file')

    parser.add_argument('-s',    '--save',             action="store_const", const=True,  help='Saves settings for experiment and trial data to current files. If trial is compiled, will append "c_" to file name and save compiled version')
    parser.add_argument('-sa', '--save_analysis', type=str, nargs="+", help='Saves analysis data, if argument specified saves to that file in path')

    parser.add_argument('-p',    '--print',            action="store_const", const=True,  help='Prints config file')

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
    

    #---> ##========>>
    if args.configure_path is not None:
        core_config["trial_path"] = args.configure_path[0]
        core_config["expt_path"] = args.configure_path[0]
        core_config["save_path"] = args.configure_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)

    if args.configure_trial_path is not None:
        core_config["trial_path"] = args.configure_trial_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.configure_trial is not None:
        core_config["trial_name"] = args.configure_trial[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    trial_config = rc.read_file(core_config["trial_path"] + core_config["trial_name"])

    if args.configure_experiment_path is not None:
        core_config["expt_path"] = args.configure_experiment_path[0]
    if args.configure_experiment is not None:
        core_config["expt_name"] = args.configure_experiment[0]
    expt_config = rc.read_file(core_config["expt_path"] + core_config["expt_name"])

    if args.configure_save_path is not None:
        core_config["save_path"] = args.configure_save_path[0]
        rc.write_file(current + CORE_FILE_NAME, core_config)
    if args.save_file is not None:
        if args.save_file[0] == "none":
            core_config["save_file"] = None
        else:
            expt_config["save_file"] = args.save_file[0]

    if args.num_trials is not None:
        expt_config["n_trials"] = args.num_trials[0]
    if args.num_processes is not None:
        expt_config["n_processes"] = args.num_processes[0]
    if args.clear_save is not None:
        expt_config["clear_save"] = bool(args.clear_save[0])
    if args.log_level is not None:
        expt_config["log_level"] = args.log_level[0]
    
    uncompiled_trial_config = deepcopy(trial_config)
    if args.compile is not None:
        trial_config = compile_as_generator(trial_config)
        

    # Save --------------------------------------------------------------------------------------------
    if args.save is not None and args.save:
        if args.compile is not None:
            temp_tc = compile_to_list(uncompiled_trial_config)
            rc.write_file(core_config["trial_path"] + "c_" + core_config["trial_name"], temp_tc)
        else:
            rc.write_file(core_config["trial_path"] + core_config["trial_name"], trial_config)
        rc.write_file(core_config["expt_path"] + core_config["expt_name"], expt_config)
    
    if args.save_trial is not None:
        if args.save_trial == "none":
            if args.compile is not None:
                temp_tc = compile_to_list(uncompiled_trial_config)
                rc.write_file(core_config["trial_path"] + "c_" + core_config["trial_name"], temp_tc)
            else:
                rc.write_file(core_config["trial_path"] + core_config["trial_name"], trial_config)
        else:
            if not isinstance(trial_config, list):
                temp_tc = compile_to_list(uncompiled_trial_config)
                rc.write_file(core_config["trial_path"] + "c_" + args.save_trial[0], temp_tc)
            else:
                rc.write_file(core_config["trial_path"] + args.save_trial[0], trial_config)
    
    if args.save_experiment is not None:
        if args.save_experiment == "none":
            rc.write_file(core_config["expt_path"] + core_config["expt_name"], expt_config)
        else:
            rc.write_file(core_config["expt_path"] + args.save_experiment[0], expt_config)

    # Print --------------------------------------------------------------------------------------------
    if args.print is not None and args.print:
        print(f'{"Core Config":-<20}')
        rc.print_config(core_config)
        print()
        print()
        print(f'{"Trial Config":-<20}')
        if isinstance(trial_config,dict):
            rc.print_config(trial_config)
        elif args.save is not None and args.save or args.save_trial is not None:
            print(temp_tc)
        else:
            print(uncompiled_trial_config)
        print()
        print()
        print(f'{"Experiment Config":-<20}')
        rc.print_config(expt_config)

    # Run --------------------------------------------------------------------------------------------
    if args.run is not None and args.run:
        expt_config["experiment"] = get_registered_experiment(expt_config["experiment"])
        if expt_config["save_file"] is not None:
            expt_config["save_file"] = core_config["save_path"] + expt_config["save_file"]
        expt = Experiment(trial_config, expt_config, expt_config["log_level"])
        print(expt.run())