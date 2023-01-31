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

if __name__=='__main__':  
    
    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',  '--run',         type=str, nargs ="+", help='Runs algorithm')
    parser.add_argument('-tr', '--num_trials',  type=int, nargs = 1,  help='Number of trials to run')
    parser.add_argument('-th', '--num_threads', type=int, nargs = 1,  help='Number of threads to run')
    parser.add_argument('-cs',  '--clear-save', type=str, nargs = 0,  help='Clears save file')
    parser.add_argument('-p',  '--print',       type=str, nargs = 0,  help='Prints config file')
    parser.add_argument('-s',  '--set',         type=str, nargs ="+", help='Sets variable in config file')
    parser.add_argument('-rs', '--reset',       type=str, nargs = 0,  help='Resets variables in config file')
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
    with open(trial_fp, "r") as f:
        trials_config = json.load(f)

   
    if hasattr(args, "print"):
        print_config_file(getattr(args,"print")[0])
    if hasattr(args, "setpath"):
        set_abs_path(getattr(args,"setpath")[0])
    if hasattr(args, "resetpath"):
        reset_abs_path()
    if hasattr(args, "replace"):
        replace_file(getattr(args,"replace")[0],getattr(args,"replace")[1])
    if hasattr(args, "merge"):
        merge_file(getattr(args,"merge"))  
    if hasattr(args, "merge-recrusive"):
        merge_file(getattr(args,"merge-recrusive"), True)  
    if hasattr(args, "update"):
        val = []
        var = []
        i = 1
        while i < len(args.update):
            val.append(getattr(args,"update")[i])
            val.append(getattr(args,"update")[i+1])
            i += 1
        update_file(val, var, getattr(args,"update")[0], True)
    if hasattr(args, "compile"):
        compile_config_file(getattr(args,"compile")[0])