#!/usr/bin/python3
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
from reconfigurator.compiler import compile_as_generator, compile_to_list

from lab_space.experiment import Experiment

import sys
import importlib.util

CORE_FILE_NAME = "/config/core/core.json"
CORE_DEFAULT_FILE_NAME = "/config/core/core_default.json"

def register_experiment(module_path, module_name, func_key_name, func_name):
    """
    Registers experiment to be run

    :param module_path: (str) Path to module
    :param module_name: (str) Name of experiment file
    :param func_key_name: (str) Key to identify function
    :param func_name: (str) Function to call register
    """

    try: 
        f = call_function(module_path, module_name, func_name)
    except:
        raise ValueError("Function not Found")

    with open(current + CORE_FILE_NAME, 'rb') as f:
        core_config = json.load(f)
        temp_dict = {
                "module_path": module_path,
                "module_name": module_name,
                "function_name": func_name
        }
        core_config["experiments"].update({func_key_name:temp_dict})
    with open(current + CORE_FILE_NAME, 'w') as f:
        json.dump(core_config, f, indent=4)

def deregister_experiment(experiment):
    """
    Deregisters experiment to be run

    :param experiment: (str) Experiment to deregister
    """
    with open(current + CORE_FILE_NAME, 'rb') as f:
        core_config = json.load(f)
        if "experiments" in core_config:
            del core_config["experiments"][experiment]
        else: 
            raise ValueError("No Registered Experiments")
    with open(current + CORE_FILE_NAME, 'w') as f:
        json.dump(core_config, f, indent=4)

def get_registered_experiment(experiment):
    """
    Gets all registered experiment

    :param experiment: (module) Experiment module
    :return: (function) Experiment function reference
    """
    with open(current + CORE_FILE_NAME, 'rb') as f:
        core_config = json.load(f)
        if "experiments" in core_config:
            expt_config = core_config["experiments"][experiment]
        else: 
            raise ValueError("No Registered Experiments")
    return call_function(expt_config["module_path"], expt_config["module_name"], expt_config["function_name"])

def call_function(module_path, module_name, func_name):
    """
    Calls function from module

    :param module_path: (str) Path to module
    :param module_name: (str) Name of experiment file
    :param func_name: (str) Function to call register
    :return: (function) Experiment function reference
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    func = getattr(module, func_name)
    return func


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',   '--run',           action="store_const", const=True,  help='Runs algorithm, if unspecified runs user default')
    
    parser.add_argument('-cr',  '--configure_reset',   action="store_const", const=True,  help='Resets all configuration to factory default')
    parser.add_argument('-cp',  '--configure_path',                 type=str, nargs = 1, help='Configures path of config and data files, if unspecified resets to factory default')
    parser.add_argument('-ctp', '--configure_trial_path',           type=str, nargs = 1, help='Configures path of trial config files, if unspecified resets to factory default')
    parser.add_argument('-ct',  '--configure_trial',                type=str, nargs = 1, help='Configures file name for trial config, if unspecified resets to factory default')
    parser.add_argument('-cep', '--configure_experiment_path',      type=str, nargs = 1, help='Configures path of experiment config files, if unspecified resets to factory default')
    parser.add_argument('-ce',  '--configure_experiment',           type=str, nargs = 1, help='Configures file name for experiment config, if unspecified resets to factory default')
    parser.add_argument('-csp', '--configure_save_path',            type=str, nargs = 1, help='Configures path of save files, if unspecified resets to factory default')
    
    parser.add_argument('-tt',  '--num_trials',                     type=int, nargs = 1,  help='Number of trials to run')
    parser.add_argument('-tp',  '--num_processes',                  type=int, nargs = 1,  help='Number of processes to run')
    parser.add_argument('-ts',  '--save_file',                      type=str, nargs ="+", help='Updates file name for save files, if unspecified resets to factory default')
    parser.add_argument('-tcs', '--clear_save',                     type=int ,nargs = 1,  help='Clears save file, 0 -> false, 1 -> true')
    parser.add_argument('-tl',  '--log_level',                      type=str, nargs = 1,  help='Sets log level')
    parser.add_argument('-tc',  '--compile',           action="store_const", const=True,  help='Compiles trial config file')

    parser.add_argument('-e',    '--experiment',                    type=str, nargs = 1,  help='Function to run')
    parser.add_argument('-er',   '--experiment_register',           type=str, nargs ="+", help='Function to register, takes 4 arguments: path, module, name, and function. If only 3 specified, current working directory will be used as path.')
    parser.add_argument('-el',   '--experiment_list',  action="store_const", const=True,  help='Lists all registered experiments')
    parser.add_argument('-ed',   '--experiment_deregister',         type=str, nargs = 1,  help='Deletes experiment from registry')
    
    parser.add_argument('-s',    '--save',             action="store_const", const=True,  help='Saves settings for experiment and trial data to current files')
    parser.add_argument('-sc',   '--save_core',                               nargs ="+", help='Saves settings for core')
    parser.add_argument('-st',   '--save_trial',                    type=str, nargs ="+", help='Saves settings for trial data, if argument specified saves to that file in path')
    parser.add_argument('-se',   '--save_experiment',               type=str, nargs ="+", help='Saves settings for experiment data, if argument specified saves to that file in path')
    
    parser.add_argument('-p',    '--print',            action="store_const", const=True,  help='Prints config file')

    args = parser.parse_args()
    print(args)
    #########################################################################################
    # Configurations ------------------------------------------------------------------------
    with open(current + CORE_FILE_NAME, "rb") as f:
        core_config = json.load(f)

    if args.experiment_deregister is not None:
        deregister_experiment(args.experiment_deregister[0])
        exit("Experiment " + args.experiment_deregister[0] + " deregistered")

    with open(current + CORE_DEFAULT_FILE_NAME, "rb") as f:
        core_default = json.load(f)

    if args.configure_reset is not None:
        with open(current + CORE_FILE_NAME, "w") as f:
            json.dump(core_default, f, indent=4)
        print("Core Reset")
    
    if args.configure_path is not None:
        core_config["trial_path"] = args.configure_path[0]
        core_config["expt_path"] = args.configure_path[0]
        core_config["save_path"] = args.configure_path[0]

    if args.configure_trial_path is not None:
        core_config["trial_path"] = args.configure_trial_path[0]
    if args.configure_trial is not None:
        core_config["trial_name"] = args.configure_trial[0]
    trial_config = rc.read_file(core_config["trial_path"] + core_config["trial_name"])

    if args.configure_experiment_path is not None:
        core_config["expt_path"] = args.configure_experiment_path[0]
    if args.configure_experiment is not None:
        core_config["expt_name"] = args.configure_experiment[0]
    expt_config = rc.read_file(core_config["expt_path"] + core_config["expt_name"])

    if args.configure_save_path is not None:
        core_config["save_path"] = args.configure_save_path[0]
    if args.save_file is not None:
        core_config["save_name"] = args.save_file[0]

    if args.num_trials is not None:
        expt_config["n_trials"] = args.num_trials[0]
    if args.num_processes is not None:
        expt_config["n_processes"] = args.num_processes[0]
    if args.clear_save is not None:
        expt_config["clear_save"] = bool(args.clear_save[0])
    if args.log_level is not None:
        expt_config["log_level"] = args.log_level[0]
    if  args.compile is not None:
        if (hasattr(args, "save") and args.save is not None) or (hasattr(args, "save_trial") and args.save_trial is not None):
            trial_config = compile_to_list(trial_config)
        else:
            trial_config = compile_as_generator(trial_config)
        

    # Function Registration -----------------------------------------------------------------
    if args.experiment is not None:
        expt_config["experiment"] = args.experiment[0]

    if args.experiment_register is not None:
        if len(args.experiment_register) == 4:
            register_experiment(args.experiment_register[0], args.experiment_register[1], args.experiment_register[2], args.experiment_register[3])
        else:
            register_experiment(os.getcwd(), args.experiment_register[1], args.experiment_register[2], args.experiment_register[3])
        # register experiment

    # Save --------------------------------------------------------------------------------------------
    if args.save is not None and args.save:
        rc.write_file(trial_config, core_config["trial_path"] + core_config["trial_name"])
        rc.write_file(expt_config, core_config["expt_path"] + core_config["expt_name"])
    if args.save_core is not None and args.save_core:
        rc.write_file(core_config, current + CORE_FILE_NAME)
    if args.save_trial is not None:
        if not len(args.save_trial):
            rc.write_file(trial_config, core_config["trial_path"] + core_config["trial_name"])
        else:
            rc.write_file(trial_config, core_config["trial_path"] + args.save_trial[0])
    if args.save_experiment is not None:
        if not len(args.save_experiment):
            rc.write_file(expt_config, core_config["expt_path"] + core_config["expt_name"])
        else:
            rc.write_file(expt_config, core_config["expt_path"] + args.save_experiment[0])

    # Print --------------------------------------------------------------------------------------------
    if args.print is not None and args.print:
        print(f'{"Core Config":-<20}')
        rc.print_config(core_config)
        print()
        print()
        print(f'{"Trial Config":-<20}')
        rc.print_config(trial_config)
        print()
        print()
        print(f'{"Experiment Config":-<20}')
        rc.print_config(expt_config)

    # Run --------------------------------------------------------------------------------------------
    if args.run is not None and args.run:
        expt_config["experiment"] = get_registered_experiment(expt_config["experiment"])
        if trial_config["save_file"] is not None:
            trial_config["save_file"] = core_config["save_path"] + trial_config["save_file"]
        expt = Experiment(trial_config, expt_config, expt_config["log_level"])
        expt.run()