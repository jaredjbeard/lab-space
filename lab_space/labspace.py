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
from reconfigurator.compile import compile_as_generator

from experiment.experiment import Experiment

import sys
import importlib.util

##########
"""
Add default saving location to config file in add cli.
"""
##########

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


def register_experiment(experiment_path, experiment_file):
    """
    Registers experiment to be run

    :param experiment_path: (str) Path to experiment file
    :param experiment_file: (str) Name of experiment file
    """
    if experiment_path is None:
        experiment_path = os.path.dirname(os.path.realpath(__file__))
    if experiment_file is None:
        experiment_file = "experiment.py"

    sys.path.append(experiment_path)
    spec = importlib.util.spec_from_file_location("experiment", os.path.join(experiment_path, experiment_file))
    experiment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(experiment)

    return experiment

def get_registered_experiment(experiment):
    """
    Gets all registered experiment

    :param experiment: (module) Experiment module
    """
    return {k:v for k,v in experiment.__dict__.items() if callable(v) and k[0] != '_'}


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',   '--run',                                  nargs = 0,  help='Runs algorithm, if unspecified runs user default')
    parser.add_argument('-up',  '--Update_path',                type=str, nargs ="+", help='Updates path of both config files, if unspecified resets to factory default')
    parser.add_argument('-utp', '--Update_trial_path',          type=str, nargs ="+", help='Updates path of trial config files, if unspecified resets to factory default')
    parser.add_argument('-ut',  '--Update_trial',               type=str, nargs ="+", help='Updates file name for trial config, if unspecified resets to factory default')
    parser.add_argument('-uep', '--Update_experiment_path',     type=str, nargs ="+", help='Updates path of experiment config files, if unspecified resets to factory default')
    parser.add_argument('-ue',  '--Update_experiment',          type=str, nargs ="+", help='Updates file name for experiment config, if unspecified resets to factory default')
    parser.add_argument('-nt',  '--num_trials',                 type=int, nargs = 1,  help='Number of trials to run')
    parser.add_argument('-np',  '--num_processes',              type=int, nargs = 1,  help='Number of processes to run')
    parser.add_argument('-cs',  '--clear-save',                 type=bool,nargs ="+", help='Clears save file, default is true')
    parser.add_argument('-l',   '--loglevel',                   type=str, nargs = 1,  help='Sets log level')
    parser.add_argument('-c',  '--compile',                               nargs = 0,  help='Compiles trial config file')

    parser.add_argument('-f',    '--function',                  type=str, nargs = 1,  help='Function to run')
    parser.add_argument('-fr',   '--function_register',         type=str, nargs = 4,  help='Function to register, takes 4 arguments: id_name, function_name, path, and module')
    
    parser.add_argument('-s',    '--save',                                nargs = 0,  help='Saves settings for experiment and trial data to current files')
    parser.add_argument('-sc',   '--save_core',                           nargs ="+", help='Saves settings for core')
    parser.add_argument('-st',   '--save_trial',                type=str, nargs ="+", help='Saves settings for trial data, if argument specified saves to that file in path')
    parser.add_argument('-se',   '--save_path',                 type=str, nargs ="+", help='Saves settings for experiment data, if argument specified saves to that file in path')
    parser.add_argument('-p',  '--print',                       type=str, nargs = 0,  help='Prints config file')

    args = parser.parse_args()

    #########################################################################################
    # Configurations ------------------------------------------------------------------------
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
    if hasattr(args, "clear_save"):
        if args.clear_save is None:
            expt_config["save"] = True
        else:
            expt_config["save"] = args.clear_save[0]
    if hasattr(args, "loglevel"):
        expt_config["loglevel"] = args.loglevel[0]
    if hasattr(args, "function"):
        expt_config["function"] = args.function[0]
    if hasattr(args, "compile"):
        trial_config = compile_as_generator(trial_config)

    # Function Registration -----------------------------------------------------------------
    if hasattr(args, "function_register"):
        register_experiment(args.function_register[0], args.function_register[1], args.function_register[2], args.function_register[3])

    # Save --------------------------------------------------------------------------------------------
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

    # Print --------------------------------------------------------------------------------------------
    if hasattr(args, "print"):
        print(f'{"Trial Config":-<20}')
        rc.print_config(trial_config)
        print(f'{"Experiment Config":-<20}')
        rc.print_config(expt_config)

    # Run --------------------------------------------------------------------------------------------
    if hasattr(args, "run"):
        expt_config["experiment"] = get_registered_experiment(expt_config["experiment"])

        expt = Experiment(trial_config, expt_config)
        expt.run()