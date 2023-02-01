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
    
    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',  '--run',         type=str, nargs ="+", help='Runs algorithm')
    parser.add_argument('-tr', '--num_trials',  type=int, nargs = 1,  help='Number of trials to run')
    parser.add_argument('-th', '--num_threads', type=int, nargs = 1,  help='Number of threads to run')
    parser.add_argument('-cs',  '--clear-save', type=str, nargs = 0,  help='Clears save file')
    parser.add_argument('-p',  '--print',       type=str, nargs = 0,  help='Prints config file')
    parser.add_argument('-st',  '--set_trial',         type=str, nargs ="+", help='Sets variable in trial config file')
    parser.add_argument('-se',  '--set_experiment',         type=str, nargs ="+", help='Sets variable in experiment config file')
    parser.add_argument('-rt', '--reset_trials',       type=str, nargs = 0,  help='Resets variables in trial config file')
    parser.add_argument('-re', '--reset_experiment',       type=str, nargs = 0,  help='Resets variables in experiment config file')
    parser.add_argument('-c',  '--compile',     type=str, nargs = 1,  help='Compiles config file')
    parser.add_argument('-l',  '--loglevel',    type=str, nargs = 1,  help='Sets log level')

    args = parser.parse_args()

    with open(current + "config/core/config.json", "r") as f:
        config = json.load(f)
    
    with open(config["expt_config"], "r") as f:
        expt_config = json.load(f)

    trial_fp = config["trials_config"]
    if hasattr(args, "run") and args.run is not None:
        trial_fp = config["trial_path"] + "/" + args.run[0]
        if len(args.run) > 1:
            trial_fp += config["save_path"] + args.run[1]
        else:
            trial_fp += config["save_path"] + config["save_file"]
    with open(trial_fp, "r") as f:
        trials_config = json.load(f)

    if hasattr(args, "print"):
        print(f'{"Trial Config":-<20}')
        rc.print_config_file(trials_config)
        print(f'{"Experiment Config":-<20}')
        rc.print_config_file(expt_config)

    if hasattr(args, "num_trials") and args.num_trials is not None:
        expt_config["num_trials"] = args.num_trials[0]
    if hasattr(args, "num_threads") and args.num_threads is not None:
        expt_config["num_threads"] = args.num_threads[0]
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


    if hasattr(args, "run"):
        expt = Experiment(trials_config, expt_config)
        expt.run()

    # Need to set core files which hold path variables
    # core default holds default values for core files and expt/trial config files
    # Need to set expt type, so we need a method to register them. 
    # Need a function to make them callable.  -> Maybe we make the CLI inheritable then users can add their own commands

    # :param trial_config: (list(dict)) Configurations for each trial 
    # :param expt_config: (dict) Experiment configuration file containing the following keys:
    #     - "experiment": (func) Reference to function under test
    #     - "is_dense": (bool) If true, will use `Reconfigurator <https://reconfigurator.readthedocs.io/en/latest/introduction.html>`_ to compile into a list of configurations, *default*: False
    #     - "n_trials": (int) Number of trials to run for each set of parameters, *default*: 1
    #     - "n_threads": (int) Number of threads to use, *default*: 1
    #     - "log_level": (str) Log level, *default*: WARNING
    #     - "file_name": (str) file to save data, if none does not save, *default*: None
    #     - "clear_save": (bool) clears data from pickle before running experiment, *default*: False