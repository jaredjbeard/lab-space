#!/usr/bin/python
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
import pickle

import nestifydict as nd


class Experiment():
    """
    Perform trials for a given set of experiments. 

    Users should provide two parameter files.

    :param trial_config: (list(dict) or generator) Configurations for each trial, *default*: None
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

        self.__lock = Lock()
        
        self._trial_config = None
        self._expt_config = None

        self.reset(trial_config, expt_config)
        
    def reset(self, trial_config = None, expt_config : dict = None):
        """
        Reset experiment with new configurations

        :param trial_config: (list(dict)) Configurations for each trial, *default*: None
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
        elif self._expt_config["clear_save"] and self._expt_config["save_file"] is not None:
            with open(self._expt_config["save_file"], 'wb') as f:
                    export_file(pd.DataFrame(), f)

        self._log.warn("Reset experiment")

    def run(self, trial_config = None, expt_config : dict = None):
        """
        Run experiment with new configurations

        :param trial_config: (list(dict)) Configurations for each trial, *default*: None
        :param expt_config: (dict) Experiment configuration, *default*: None
        :return: (pandas.DataFrame) data
        """
        if trial_config is not None or expt_config is not None:
            self.reset(trial_config, expt_config)

        if self._trial_config is None:
            raise ValueError("Must provide trial configuration")
        if self._expt_config["experiment"] is None:
            raise ValueError("Must provide experiment function")

        self._log.warn("Run experiment")
        self._results = []

        if self._expt_config["n_processes"] == 1:
            return self._run_single()
        return self._run_multi()

    def _run_single(self):
        """
        Run experiment in single thread

        :return: (pandas.DataFrame) data
        """
        self._log.warn("Run experiment in single thread")
        results = []
        for trial in self.__n_iterable(self._trial_config, self._expt_config["n_trials"]):
            if self._expt_config["save_file"] is not None:
                results.append(self._run_save(trial))
            results.append(self._expt_config["experiment"](trial))
        return results

    def _run_multi(self):
        """
        Run experiment in multiple processes

        :return: (pandas.DataFrame) data
        """
        self._log.warn("Run experiment in multiple processes")
        with Pool(self._expt_config["n_processes"]) as p:
            if self._expt_config["save_file"] is not None:
                return p.map(self._run_save, self._n_iterable(self._trial_config, self._expt_config["n_trials"]))
            return p.map(self._expt_config["experiment"], self._n_iterable(self._trial_config, self._expt_config["n_trials"]))

    def _run_save(self, trial_config):
        """
        Run experiment and save results

        :param trial_config: (list(dict)) Configurations for each trial
        :return: (pandas.DataFrame) data
        """
        result = self._expt_config["experiment"](trial_config)
        with self.__lock:
            data = import_file(self._expt_config["save_file"])
            pd.concat([data, result])
            export_file(data,self._expt_config["save_file"])
        return result

    def __n_iterable(self, iterable_el, n = 1):
        """
        Return n copies of an iterable

        :param iterable_el: (iterable) Iterable to copy
        :param n: (int) Number of copies
        :return: () n copies of the input sequences
        """
        for element in itertools.repeat(iterable_el, n):
            for el in element:
                yield el

def import_file(filepath):
    """
    Import a file as a Pandas dataframe based on its file extension

    :param filepath: (str) file path
    :return: (pandas.DataFrame) the imported dataframe
    """
    extension = filepath.split(".")[-1]
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
