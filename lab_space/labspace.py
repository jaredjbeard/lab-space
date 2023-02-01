#!/usr/bin/python
"""
This script is handle command line argmuents for starting experiments and analyzing data.
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

import argparse
import json
import reconfigurator.reconfigurator as rc

from experiment.experiment import Experiment

import sys
import importlib.util


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',   '--run',                              nargs = 0,  help='Runs algorithm, if unspecified runs user default')
    parser.add_argument('-up',  '--Update_path',               type=str, nargs ="+", help='Updates path of both config files, if unspecified resets to factory default')
    parser.add_argument('-utp', '--Update_trial_path',         type=str, nargs ="+", help='Updates path of trial config files, if unspecified resets to factory default')
    parser.add_argument('-ut',  '--Update_trial',              type=str, nargs ="+", help='Updates file name for trial config, if unspecified resets to factory default')
    parser.add_argument('-uep', '--Update_experiment_path',    type=str, nargs ="+", help='Updates path of experiment config files, if unspecified resets to factory default')
    parser.add_argument('-ue',  '--Update_experiment',         type=str, nargs ="+", help='Updates file name for experiment config, if unspecified resets to factory default')
    parser.add_argument('-nt',  '--num_trials',             type=int, nargs = 1,  help='Number of trials to run')
    parser.add_argument('-np',  '--num_processes',          type=int, nargs = 1,  help='Number of processes to run')

    parser.add_argument('-s',    '--save',                             nargs = 0,  help='Saves settings for experiment and trial data to current files')
    parser.add_argument('-sc',   '--save_core',                       nargs ="+",  help='Saves settings for core')
    parser.add_argument('-st',   '--save_trial',            type=str, nargs ="+",  help='Saves settings for trial data, if argument specified saves to that file in path')
    parser.add_argument('-se',   '--save_path',             type=str, nargs ="+",  help='Saves settings for experiment data, if argument specified saves to that file in path')


    args = parser.parse_args()

    #########################################################################################
    with open(current + "config/core/core.json", "r") as f:
        core_config = json.load(f)
    with open(current + "config/core/core_default.json", "r") as f:
        core_default = json.load(f)

    if hasattr(args, "update_path"):
        if args.update_path is None:
            core_config["trial_path"] = core_default["trial_path"]
            core_config["expt_path"] = core_default["expt_path"]
        else:
            core_config["trial_path"] = args.update_path[0]
            core_config["expt_path"] = args.update_path[0]

    if hasattr(args, "update_trial_path"):
        if args.update_trial_path is None:
            core_config["trial_path"] = core_default["trial_path"]
        core_config["trial_path"] = args.trial_path[0]

    if hasattr(args, "update_trial"):
        if args.update_trial is None:
            core_config["trial_name"] = core_default["trial_name"]
        core_config["trial_name"] = args.trial[0]
    trial_config = rc.read_file(core_config["trial_path"] + core_config["trial_name"])
    
    if hasattr(args, "update_experiment_path"):
        if args.update_experiment_path is None:
            core_config["expt_path"] = core_default["expt_path"]
        core_config["expt_path"] = args.experiment_path[0]
    if hasattr(args, "update_experiment"):
        if args.update_experiment is None:
            core_config["expt_name"] = core_default["expt_name"]
        core_config["expt_name"] = args.experiment[0]
    expt_config = rc.read_file(core_config["expt_path"] + core_config["expt_name"])

    if hasattr(args, "num_trials"):
        expt_config["num_trials"] = args.num_trials[0]
    if hasattr(args, "num_processes"):
        expt_config["num_processes"] = args.num_processes[0]



    if hasattr(args, "save"):
        rc.write_file(trial_config, core_config["trial_path"] + core_config["trial_name"])
        rc.write_file(expt_config, core_config["expt_path"] + core_config["expt_name"])
    if hasattr(args, "save_core"):
        rc.write_file(core_config, current + "config/core/core.json")
    if hasattr(args, "save_trial"):
        if args.save_trial is None:
            rc.write_file(trial_config, core_config["trial_path"] + core_config["trial_name"])
        else:
            rc.write_file(trial_config, core_config["trial_path"] + args.save_trial[0])
    if hasattr(args, "save_experiment"):
        if args.save_experiment is None:
            rc.write_file(expt_config, core_config["expt_path"] + core_config["expt_name"])
        else:
            rc.write_file(expt_config, core_config["expt_path"] + args.save_experiment[0])

    if hasattr(args, "run"):
        expt = Experiment(trials_config, expt_config)
        expt.run()

# add core defaults to config file in add cli. 
### Need to also test whether the function is callable.
# def call_function(module_path, module_name, func_name, *args):
#     spec = importlib.util.spec_from_file_location(module_name, module_path)
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[module_name] = module
#     spec.loader.exec_module(module)
#     func = getattr(module, func_name)
#     return func(*args)

# module_path = 'path/to/my_functions.py'
# module_name = 'my_functions'
# functions = {
#     'add': (module_path, module_name, 'add')
# }

# func_name = 'add'
# module_path, module_name, func_name = functions[func_name]
# result = call_function(module_path, module_name, func_name, 3, 4)
# print(result)  # Output: 7

## I should add a register function. 

if __name__=='__main__':  

    # Desired functionality: 
    """
    For both trial and experiment. Have option to set path for both at same time or separately.
    Users can optionally set trial or expt config file names. -tr , -ex, if trial needs compiled, -c.
    Users can overwrite the function -f, num processes -nt, num trials -tr, and num experiments -ex, -ll log level
    Users can also print the current config file with -p.
    Users can also clear the save file with -cs.

    Users can also register a new trial function. 
    """
    parser.add_argument('-cs',  '--clear-save', type=str, nargs = 0,  help='Clears save file')
    parser.add_argument('-p',  '--print',       type=str, nargs = 0,  help='Prints config file')
    parser.add_argument('-rt', '--reset_trials',       type=str, nargs = 0,  help='Resets variables in trial config file')
    parser.add_argument('-re', '--reset_experiment',       type=str, nargs = 0,  help='Resets variables in experiment config file')
    parser.add_argument('-c',  '--compile',     type=str, nargs = 1,  help='Compiles config file')
    parser.add_argument('-l',  '--loglevel',    type=str, nargs = 1,  help='Sets log level')

    #-o overwrite params with current config 


    # if hasattr(args, "run") and args.run is None:
        

    # trial_fp = core_config["trial_path"] + core_config["trial_name"]
    
    #     trial_fp = config["trial_path"] + "/" + args.run[0]
    #     if len(args.run) > 1:
    #         trial_fp += config["save_path"] + args.run[1]
    #     else:
    #         trial_fp += config["save_path"] + config["save_file"]
    # with open(trial_fp, "r") as f:
    #     trials_config = json.load(f)

    # with open(core_config["expt_path"] + core_config["expt_path"], "r") as f:
    #     expt_config = json.load(f)
    
   

    if hasattr(args, "print"):
        print(f'{"Trial Config":-<20}')
        rc.print_config_file(trials_config)
        print(f'{"Experiment Config":-<20}')
        rc.print_config_file(expt_config)

    if hasattr(args, "num_trials") and args.num_trials is not None:
        expt_config["num_trials"] = args.num_trials[0]
    if hasattr(args, "num_processes") and args.num_processes is not None:
        expt_config["num_processes"] = args.num_processes[0]
    if hasattr(args, "clear-save") and args.clear_save is not None:
        expt_config["clear_save"] = True
    if hasattr(args, "print"):
        print(f'{"Trial Config":-<20}')
        rc.print_config_file(trials_config)
        print(f'{"Experiment Config":-<20}')
        rc.print_config_file(expt_config)

    if hasattr(args, "reset_trials"):
        val = []
        var = []
        i = 1
        while i < len(args.set_trial):
            val.append(getattr(args,"reset_trials")[i])
            val.append(getattr(args,"reset_trials")[i+1])
            i += 1
        rc.update_file(val, var, getattr(args,"set_trial")[0], True)
    
    if hasattr(args, "reset_experiment"):
        val = []
        var = []
        i = 1
        while i < len(args.set_experiment):
            val.append(getattr(args,"reset_experiment")[i])
            val.append(getattr(args,"reset_experiment")[i+1])
            i += 1
        rc.update_file(val, var, getattr(args,"set_experiment")[0], True)

    if hasattr(args, "reset_trial"):
        default_trials_config = rc.read_file("config/core/core_default.json")["trials_config"]
        rc.write_file(trial_fp, default_trials_config)
    if hasattr(args, "reset_experiment"):
        default_expt_config = rc.read_file("config/core/core_default.json")["expt_config"]
        rc.write_file(config["expt_config"], default_expt_config)
    if 

    parser.add_argument('-rs', '--reset',       type=str, nargs = 0,  help='Resets variables in config file')
    parser.add_argument('-c',  '--compile',     type=str, nargs = 1,  help='Compiles config file')
    parser.add_argument('-l',  '--loglevel',    type=str, nargs = 1,  help='Sets log level')


    

    # Need to set core files which hold path variables
    # core default holds default values for core files and expt/trial config files
    # Need to set expt type, so we need a method to register them. 
    # Need a function to make them callable.  -> Maybe we make the CLI inheritable then users can add their own commands

    # :param trial_config: (list(dict)) Configurations for each trial 
    # :param expt_config: (dict) Experiment configuration file containing the following keys:
    #     - "experiment": (func) Reference to function under test
    #     - "is_dense": (bool) If true, will use `Reconfigurator <https://reconfigurator.readthedocs.io/en/latest/introduction.html>`_ to compile into a list of configurations, *default*: False
    #     - "n_trials": (int) Number of trials to run for each set of parameters, *default*: 1
    #     - "n_processes": (int) Number of processes to use, *default*: 1
    #     - "log_level": (str) Log level, *default*: WARNING
    #     - "file_name": (str) file to save data, if none does not save, *default*: None
    #     - "clear_save": (bool) clears data from pickle before running experiment, *default*: False

    # Make an experiment that tweaks experiment after it runs to learn...