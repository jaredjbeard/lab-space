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
from reconfigurator.compiler import compile_as_generator
from copy import deepcopy

from file_utils import *

import nestifydict as nd


class Analysis():
    """
    Analyses a set of data.

    With regard to saving, in the <save_path> folder, analysis will add a folder for the given day and time. Within this, it will create the following files:
        - <save_file>.csv: The data used for the analysis
        - <save_file>.pkl: The figures from the analysis
        - <save_file>.png: The figures from the analysis
        - <save_file>.eps: The figures from the analysis

    :param analysis_config: (dict) Analysis configuration containing the following keys:
        - "data_file: (str) Path of data file (csv or xcls)
        - "save_path": (str) Path to save figures to
        - "save_file": (str) Path of save file (do not include extension, figures will be saved as .png, .eps, and .pkl)
        - "type": (str) type of figures to generate (can be a list). options include line, contour
        - "fig_params": (dict) Parameters for figure generation for each figure
        - "cross_ref": (str) Name of column to cross reference data by (these are what you will see in the legends)
        - "ind_var": (str) Name of column to use as independent variable
        - "dep_var": (str) Name of column to use as dependent variable
        - "control_var": (str) Name of column to use as control variable (this will generate subplots for each value, or if there are too many, will bin them)
    :param log_level: (str) Logging level, *default*: "WARNING"
    """
    def __init__(self, analysis_config : dict = None, log_level : str = "WARNING"):
        
        super(Analysis, self).__init__()
        
        log_levels = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR ,"CRITICAL": logging.CRITICAL}
        self._log_level = log_levels[log_level]
                                             
        logging.basicConfig(stream=sys.stdout, format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=self._log_level)
        self._log = logging.getLogger(__name__)
        
        self._log.warn("Analysis Init")

        self._analysis_config = {}

        self.reset(analysis_config)
        
    def reset(self, analysis_config : dict = None):
        """
        Reset analysis with new configurations

        :param analysis_config: (dict) Analysis configuration, *default*: None
        """
        
        if analysis_config is not None:
            self._analysis_config = nd.merge(self._analysis_config, analysis_config)

        if "data_file" not in self._expt_config or self._expt_config["data_file"] is None:
            raise ValueError("Must provide data file")
        if "save_file" not in self._expt_config or self._expt_config["save_file"] is None:
            raise ValueError("Must provide save file")
        if "save_path" not in self._expt_config or self._expt_config["save_path"] is None:
            raise ValueError("Must provide save path")
        if "type" not in self._expt_config or self._expt_config["type"] is None:
            self._analysis_config["type"] = "line"
        if "fig_params" not in self._expt_config or self._expt_config["fig_params"] is None:
            self._analysis_config["fig_params"] = {}
        if "cross_ref" not in self._expt_config:
            raise ValueError("Must provide cross reference variable")
        if "ind_var" not in self._expt_config or self._expt_config["ind_var"] is None:
            raise ValueError("Must provide independent variable")   
        if "dep_var" not in self._expt_config or self._expt_config["dep_var"] is None:
            raise ValueError("Must provide dependent variable")
        if "control_var" not in self._expt_config:
            self._analysis_config["control_var"] = None

        self._log.warn("Reset experiment")

    def run(self, analysis_config : dict = None):
        """
        Run analysis

        :param analysis_config: (dict) Analysis configuration, *default*: None
        """
        if analysis_config is not None:
            self.reset(analysis_config)

        data = import_file(self._analysis_config["data_file"])

        data = self._get_analysis_cols(data)

        self._manip_data = self.cross_reference(data)

        self._manip_data = self.split_dependence(self._manip_data)

        # Extract relevant indep/dep variables

        # split into control groups

        # Process data

        # plot

        # save

    def _get_analysis_cols(self, data):
        """
        Extracts columns relevant to analysis

        :param data: (pandas.DataFrame) Unfiltered data 
        :return: (pandas.DataFrame) Data with relevant columns
        """
        needed_cols = [self._analysis_config["cross_ref"], self._analysis_config["ind_var"], self._analysis_config["dep_var"], self._analysis_config["control_var"]]
        for i, el in enumerate(needed_cols):
            if isinstance(el,dict):
                needed_cols[i] = el["var"]

        # Add aliased vars to needed cols

        return data[needed_cols]

    
    def cross_reference(self, data):
        """
        Cross reference data by a given column

        :param data: (pandas.DataFrame) Data to cross reference
        :return: (pandas.DataFrame) Cross referenced data
        """
        if not isinstance(self._analysis_config["cross_ref"], dict):
            return data.groupby(self._analysis_config["cross_ref"])
        else:
            drop_nan = False
            if "drop_nan" in self._analysis_config["cross_ref"] and self._analysis_config["cross_ref"]["drop_nan"]:
                drop_nan = True
            return data.groupby(self._analysis_config["cross_ref"]["var"], dropna=drop_nan)

    def split_dependence(self, data):
        """
        Split data by dependent and independent variables

        :param data: (pandas.DataFrame) Data to split
        :return: (pandas.DataFrame) Split data
        """
        if not isinstance(self._analysis_config["dep_var"], dict):
            return data.groupby(self._analysis_config["dep_var"])
        else:
            drop_nan = False
            if "drop_nan" in self._analysis_config["dep_var"] and self._analysis_config["dep_var"]["drop_nan"]:
                drop_nan = True
            return data.groupby(self._analysis_config["dep_var"]["var"], dropna=drop_nan)

    def get_plot():
        pass
    #gets plot type from string

    def setup_subplots():
        pass
        #based on number of plots desired arranges subplots
