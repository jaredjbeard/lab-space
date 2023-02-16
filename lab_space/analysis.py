#!/usr/bin/env python3
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

        if "data_file" not in self._analysis_config or self._analysis_config["data_file"] is None:
            raise ValueError("Must provide data file")
        if "save_file" not in self._analysis_config or self._analysis_config["save_file"] is None:
            raise ValueError("Must provide save file")
        if "save_path" not in self._analysis_config or self._analysis_config["save_path"] is None:
            raise ValueError("Must provide save path")
        if "type" not in self._analysis_config or self._analysis_config["type"] is None:
            self._analysis_config["type"] = "line"
        if "fig_params" not in self._analysis_config or self._analysis_config["fig_params"] is None:
            self._analysis_config["fig_params"] = {}
        if "cross_ref" not in self._analysis_config:
            raise ValueError("Must provide cross reference variable")
        if "ind_var" not in self._analysis_config or self._analysis_config["ind_var"] is None:
            raise ValueError("Must provide independent variable")   
        if "dep_var" not in self._analysis_config or self._analysis_config["dep_var"] is None:
            raise ValueError("Must provide dependent variable")
        if "control_var" not in self._analysis_config:
            self._analysis_config["control_var"] = None

        self._log.warn("Reset experiment")

    def analyze(self, analysis_config : dict = None):
        """
        Run analysis

        :param analysis_config: (dict) Analysis configuration, *default*: None
        """
        if analysis_config is not None:
            self.reset(analysis_config)

        data = import_file(self._analysis_config["data_file"])

        if "filter" not in self._analysis_config:
            self._analysis_config["filter"] = {}
        if "include_cols" not in self._analysis_config["filter"]:
            self._analysis_config["filter"]["include_cols"] = []
        
        if "rm_unused_cols" in self._analysis_config["filter"] and self._analysis_config["filter"]["rm_unused_cols"]:
            self.rm_unused_cols()
        
        data = filter_data(data, self._analysis_config["filter"])

        print(data)

        self._manip_data = self.cross_reference(data)

        print(self._manip_data.groups)
        print(self._manip_data.get_group("a"))

        # self._manip_data = self.split_data(self._manip_data)

        # split into control groups

        # Process data

        # plot

        # save

        # let users pass in kwargs using dictionary to various pd functions

    def rm_unused_cols(self):
        """
        Remove unused columns from data

        :param data: (pandas.DataFrame) Data to remove unused columns from
        :return: (pandas.DataFrame) Data with unused columns removed
        """
        cols = [self._analysis_config["ind_var"], self._analysis_config["dep_var"]]
        if self._analysis_config["cross_ref"] is not None:
            cols.append(self._analysis_config["cross_ref"])
        if self._analysis_config["control_var"] is not None:
            cols.append(self._analysis_config["control_var"])
        self._analysis_config["filter"]["include_cols"] += cols

    def cross_reference(self, data):
        """
        Cross reference data by a given column

        :param data: (pandas.DataFrame) Data to cross reference
        :return: (pandas.DataFrame) Cross referenced data
        """

        #if not dict, convert to dicitionary with name as key and list of data frames as "df"

        # otherwise if names in dict, add these to names, else generate from conditions
        # for each el in key (unless empty, then replace with all), then attempt to make data frame from col
        # if col is a dict, then try filter data recursively to generate a data frame. 
        # (may desire to remove shared values)

        if not isinstance(self._analysis_config["cross_ref"], dict):
            return data.groupby(self._analysis_config["cross_ref"])
        else:
            drop_nan = False
            if "drop_nan" in self._analysis_config["cross_ref"] and self._analysis_config["cross_ref"]["drop_nan"]:
                drop_nan = True
            return data.groupby(self._analysis_config["cross_ref"]["var"], dropna=drop_nan)

    def split_data(self, grouped_data):
        """
        Split grouped data into corresponding data frames for each group.

        :param grouped_data: (pd.core.groupby.GroupBy) Grouped data to split
        :return: (dict) Dictionary mapping group keys to corresponding data frames
        """
        dep_var = self._analysis_config["dep_var"]
        indep_var = self._analysis_config["indep_var"]
        result = {}
        for group, data in grouped_data:
            result[group] = pd.DataFrame(data={"dependent": data[dep_var], "independent": data[indep_var]})
        return result


def filter_data(data, filter_config):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param filter_config: (dict) Filter configuration containing the following keys:
    :return: (pd.DataFrame) filtered data
    """
    if "include_cols" in filter_config and filter_config["include_cols"] is not None:
        data = include_cols_filter(data, filter_config["include_cols"])
    if "exclude_cols" in filter_config and filter_config["exclude_cols"] is not None:
        data = exclude_cols_filter(data, filter_config["exclude_cols"])

    if "include_vals" in filter_config and filter_config["include_vals"] is not None:
        data = include_vals_filter(data, filter_config["include_vals"])
    if "exclude_vals" in filter_config and filter_config["exclude_vals"] is not None:
        data = exclude_vals_filter(data, filter_config["exclude_vals"])
    return data

def include_vals_filter(data, include_els):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param include_els: (dict) Dictionary of columns and values to include
    :return: (pd.DataFrame) filtered data
    """
    temp_data = pd.DataFrame()
    for col in include_els.keys():
        if include_els[col] == []:
            include_vals = data[col].unique()
        else:
            include_vals = include_els[col]
        if isinstance(include_vals, list):
            if include_vals[0] == "":
                include_vals[0] = data[col].min()
            if include_vals[1] == "":
                include_vals[1] = data[col].max()
            temp_data = pd.concat([temp_data, data[data[col].between(include_vals[0], include_vals[1], inclusive=True)]])
        else:
            temp_data = pd.concat([temp_data, data[data[col].isin(include_vals)]])
    return temp_data

def exclude_vals_filter(data, exclude_els):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param exclude_els: (dict) Dictionary of columns and values to exclude
    :return: (pd.DataFrame) filtered data
    """
    temp_data = pd.DataFrame()
    for col in exclude_els.keys():
        if exclude_els[col] == []:
            exclude_vals = data[col].unique()
        else:
            exclude_vals = exclude_els[col]
        if col in data.columns:
            temp_data = pd.concat([temp_data, data[~data[col].isin(exclude_vals)]])
    return temp_data

def include_cols_filter(data, include_cols):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param include_cols: (list) List of columns to include
    :return: (pd.DataFrame) filtered data
    """
    return data[include_cols]

def exclude_cols_filter(data, exclude_cols):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param exclude_cols: (list) List of columns to exclude
    :return: (pd.DataFrame) filtered data
    """
    return data.drop(exclude_cols, axis=1)