#!/usr/bin/python3
"""
This script is intended to run single or multithreaded experiments.
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

from multiprocessing import Pool, Lock
import logging
import itertools
import pandas as pd
from reconfigurator.reconfigurator import compile_as_generator
from copy import deepcopy

import nestifydict as nd


class Experiment():
    """
    Perform trials for a given set of experiments. 

    Users should provide two parameter files.

    :param trial_config: (list(dict)/generator) Configurations for each trial, *default*: None
    :param expt_config: (dict) Experiment configuration file containing the following keys:
        - *default*: None
        - "experiment": (func) Reference to function under test
        - "n_trials": (int) Number of trials to run for each set of parameters, *default*: 1
        - "n_processes": (int) Number of processes to use, *default*: 1
        - "save_file": (str) file to save data, if none does not save, *default*: None
        - "clear_save": (bool) clears data from pickle before running experiment, *default*: False
    :param log_level: (str) Logging level, *default*: "WARNING"
    """
    def __init__(self, trial_config = None, expt_config : dict = None, log_level : str = "WARNING"):
        
        super(Experiment, self).__init__()
        
        log_levels = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR ,"CRITICAL": logging.CRITICAL}
        self._log_level = log_levels[log_level]
                                             
        logging.basicConfig(stream=sys.stdout, format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=self._log_level)
        self._log = logging.getLogger(__name__)
        
        self._log.warn("RunExperiment Init, perform " + str(expt_config["n_trials"]) + " trials across " + str(expt_config["n_processes"]) + " processes")

        global expt_lock
        expt_lock = Lock()
        
        self._trial_config = []
        self._expt_config = {}

        self.reset(trial_config, expt_config)
        
    def reset(self, trial_config = None, expt_config : dict = None):
        """
        Reset experiment with new configurations

        :param trial_config: (list(dict)/generator) Configurations for each trial, *default*: None
        :param expt_config: (dict) Experiment configuration, *default*: None
        """
        
        if trial_config is not None:
            self._trial_config = trial_config
        if expt_config is not None:
            self._expt_config = nd.merge(self._expt_config, expt_config)

        if "experiment" not in self._expt_config:
            raise ValueError("Must provide experiment function")
        if "n_trials" not in self._expt_config:
            self._expt_config["n_trials"] = 1
        if "n_processes" not in self._expt_config:
            self._expt_config["n_processes"] = 1
        if "save_file" not in self._expt_config:
            self._expt_config["save_file"] = None
        if "clear_save" not in self._expt_config:
            self._expt_config["clear_save"] = False
        if self._expt_config["clear_save"] and self._expt_config["save_file"] is not None and os.path.isfile(self._expt_config["save_file"]):
            self._log.warn("Clearing save file")
            os.remove(self._expt_config["save_file"])

        self._log.warn("Reset experiment")

    def run(self, trial_config = None, expt_config : dict = None):
        """
        Run experiment with new configurations

        :param trial_config: (list(dict)/generator) Configurations for each trial, *default*: None
        :param expt_config: (dict) Experiment configuration, *default*: None
        :return: (pandas.DataFrame) data
        """
        if trial_config is not None or expt_config is not None:
            self.reset(trial_config, expt_config)

        if self._trial_config == []:
            raise ValueError("Must provide trial configuration")
        if self._expt_config["experiment"] == {}:
            raise ValueError("Must provide experiment function")

    def get_plot():
        pass
    #gets plot type from string

    def setup_subplots():
        pass
        #based on number of plots desired arranges subplots

def import_file(filepath):
    """
    Import a file as a Pandas dataframe based on its file extension

    :param filepath: (str) file path
    :return: (pandas.DataFrame) the imported dataframe
    """
    extension = filepath.split(".")[-1]
    if not os.path.isfile(filepath):
        return pd.DataFrame()
    if extension == "csv":
        return pd.read_csv(filepath)
    elif extension == "xlsx":
        return pd.read_excel(filepath)
    elif extension == "json":
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

def export_file(df, filepath):
    """
    Write a Pandas dataframe to a file based on its file extension

    :param df: (pandas.DataFrame) the dataframe to be written
    :param filepath: (str) file path
    :return: None
    """
    extension = filepath.split(".")[-1]
    if extension == "csv":
        df.to_csv(filepath, index=False)
    elif extension == "xlsx":
        df.to_excel(filepath, index=False)
    elif extension == "json":
        df.to_json(filepath, index=False)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

def check_and_create_file(file_path):
    file_extension = os.path.splitext(file_path)[1]
    if not os.path.exists(file_path):
        empty_df = pd.DataFrame()
        if file_extension == '.csv':
            empty_df.to_csv(file_path, index=False)
        elif file_extension == '.json':
            empty_df.to_json(file_path)
        elif file_extension == '.xlsx':
            empty_df.to_excel(file_path, index=False)
        else:
            return "Invalid file type"
        return "Empty file created at: " + file_path
    return "File already exists at: " + file_path
