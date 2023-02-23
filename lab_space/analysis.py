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
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt
from reconfigurator.compiler import compile_as_generator
from copy import deepcopy

from file_utils import *

import nestifydict as nd

class Analysis():
    """
    Analyses a set of data.

    With regard to saving, in the <figure_path> folder, analysis will add a folder for the given day and time. Within this, it will create the following files:
        - <figure_file>.pkl: The data and figures from the analysis
        - <figure_file>.png: The figures from the analysis
        - <figure_file>.eps: The figures from the analysis

    :param analysis_config: (dict) Analysis configuration containing the following keys:
        - "data_file: (str) Path of data file (csv or xcls)
        - "figure_path": (str) Path to save figures to
        - "figure_file": (str) Path of save file (do not include extension, figures will be saved as .png, .eps, and .pkl)
        - "type": (str) type of figures to generate (can be a list). options include line, contour
        - "fig_params": (dict) Parameters for figure generation for each figure
        - "cross_ref": (str) Name of column to cross reference data by (these are what you will see in the legends)
        - "x": (str) Name of column to use as independent variable
        - "y": (str) Name of column to use as dependent variable
        - "control": (str) Name of column to use as control variable (this will generate subplots for each value, or if there are too many, will bin them)
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
        if "figure_file" not in self._analysis_config or self._analysis_config["figure_file"] is None:
            raise ValueError("Must provide save file")
        if "figure_path" not in self._analysis_config or self._analysis_config["figure_path"] is None:
            raise ValueError("Must provide save path")
        if "type" not in self._analysis_config or self._analysis_config["type"] is None:
            self._analysis_config["type"] = "line"
        if "fig_params" not in self._analysis_config or self._analysis_config["fig_params"] is None:
            self._analysis_config["fig_params"] = {}
        if "cross_ref" not in self._analysis_config:
            raise ValueError("Must provide cross reference variable")
        if "x" not in self._analysis_config or self._analysis_config["x"] is None:
            raise ValueError("Must provide independent variable")   
        if "y" not in self._analysis_config or self._analysis_config["y"] is None:
            raise ValueError("Must provide dependent variable")
        if "control" not in self._analysis_config:
            self._analysis_config["control"] = None

        self._log.warn("Reset experiment")

    def run(self, analysis_config : dict = None):
        """
        Run analysis

        :param analysis_config: (dict) Analysis configuration, *default*: None
        """
        if analysis_config is not None:
            self.reset(analysis_config)

        data = import_file(self._analysis_config["data_file"])
        
        if "merge_cols" in self._analysis_config:
            data = merge_cols(data, self._analysis_config["merge_cols"])

        if "filter" not in self._analysis_config:
            self._analysis_config["filter"] = {}
        # if "include_cols" not in self._analysis_config["filter"]:
        #     self._analysis_config["filter"]["include_cols"] = []
        
        if "rm_unused_cols" in self._analysis_config["filter"] and self._analysis_config["filter"]["rm_unused_cols"]:
            self.rm_unused_cols()
        
        data = filter_data(data, self._analysis_config["filter"])

        self.compile_bins(data)
        
        cr_data = self.cross_reference(data)
        
        # for el in cr_data:
        #     print("-----------------")
        #     print(el["legend"])
        #     print(el["data"])
            
        

        split_data = self.split_data(cr_data)
        
        # print("-----Plot Data-----")
        # for el in split_data:
        #     print("-----------------")
        #     print(split_data[el])
        
        
        plt_data = self.plot(split_data)
        
    def rm_unused_cols(self):
        """
        Remove unused columns from data

        :param data: (pandas.DataFrame) Data to remove unused columns from
        :return: (pandas.DataFrame) Data with unused columns removed
        """
        cols = [self._analysis_config["x"], self._analysis_config["y"]]
        if self._analysis_config["cross_ref"] is not None:
            cols.append(self._analysis_config["cross_ref"])
        if self._analysis_config["control"] is not None:
            cols.append(self._analysis_config["control"])
        self._analysis_config["filter"]["include_cols"] += cols

    def cross_reference(self, data : pd.DataFrame):
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
            grouped_data = data.groupby(self._analysis_config["cross_ref"])
            elements = []
            for group in grouped_data.groups:
                elements.append({"legend": group, "data": grouped_data.get_group(group)})
            return elements
        else:
            elements = []
            for name, logic in zip(self._analysis_config["cross_ref"]["name"], self._analysis_config["logic"]):
                elements.append({"legend": name, "data": data[data_logic(data, logic)]})

    def split_data(self, grouped_data : list):
        """
        Split grouped data into corresponding data frames for each group.

        :param grouped_data: (list) Grouped data to split
        :return: (dict) List of dictionaries containing legend and data
        """
        if "z" not in self._analysis_config:
            self._analysis_config["z"] = None
        
        plot_data = {"plot": ["all"], "data": []}
        split_data = []
        
        for el in grouped_data:
            include_cols = [ self._analysis_config["x"], self._analysis_config["y"]]
            if self._analysis_config["z"] is not None:
                include_cols.append(self._analysis_config["z"])
            if self._analysis_config["control"] is not None:
                include_cols.append(self._analysis_config["control"])
            temp = {"legend": el["legend"], "data": include_cols_filter(el["data"], include_cols)}
            split_data.append(temp)
                
        plot_data["data"].append(split_data)
        
        if self._analysis_config["control"] is not None:      
            for name, bin in zip(self._analysis_config["control_kwargs"]["names"], self._analysis_config["control_kwargs"]["bins"]):
                temp_data = []
                for el in split_data:
                    temp_data.append({"legend": el["legend"], "data" : el["data"][data_logic(el["data"], bin)]})
                plot_data["plot"].append(name)
                plot_data["data"].append(temp_data)
        
        return plot_data
    
    def compile_bins(self, data : pd.DataFrame):
        """
        Compile bins for control variable from markup specification
        
        :param data: (pandas.DataFrame) Data to compile bins from
        """
        if "control" not in self._analysis_config:
            self._analysis_config["control"] = None
        if self._analysis_config["control"] is not None:
            if "control_kwargs" not in self._analysis_config:
                self._analysis_config["control_kwargs"] = {}
            if not "bins" in self._analysis_config["control_kwargs"]:
                self._analysis_config["control_kwargs"]["bins"] = {}
            if "bins" not in self._analysis_config["control_kwargs"]["bins"]:
                self._analysis_config["control_kwargs"]["bins"].update({"bins" : data[self._analysis_config["control"]].unique().tolist()})
            if "as_interval" not in self._analysis_config["control_kwargs"]["bins"]:
                self._analysis_config["control_kwargs"]["bins"].update({"as_interval" : True})
            bin_names, control_bins = bin_control(data, self._analysis_config["control"], self._analysis_config["control_kwargs"]["bins"])
            self._analysis_config["control_kwargs"] = {"names": bin_names, "bins": control_bins}
            
    def plot(self, data : list):
        """
        Plots data provided by list of plot data dictionaries.
        
        :param data: (list) List of plot data dictionaries
        :return: (list) List of plot data dictionaries and figures
        """
        if "kwargs" not in self._analysis_config["fig"] or self._analysis_config["fig"]["kwargs"] is None:
            self._analysis_config["fig"]["kwargs"] = {}
        if len(data) > 1:
            num_plots = len(data["plot"])
        else:
            num_plots = 1

        splt_len = [int(np.ceil(np.sqrt(num_plots))), int(np.floor(np.sqrt(num_plots)))]
        if splt_len[0]*splt_len[1] < num_plots:
            splt_len = [int(np.ceil(np.sqrt(num_plots))), int(np.ceil(np.sqrt(num_plots)))]
        fig, ax = plt.subplots(splt_len[0],splt_len[1],figsize=(7.5, 7.5 ))
        print(num_plots, splt_len)
        splt_x = 0
        splt_y = 0
        
        fignum = fig.number
        
        for i in range(num_plots):
            if data["plot"][i] == "all":
                data["plot"][i] = self._analysis_config["fig"]["title"]
            #series (legend) loop
            plt_legend = []
            for j in range(len(data["data"][i])):
                plt_legend.append(data["data"][i][j]["legend"])
            for j in range(len(data["data"][i])):
                subset = data["data"][i][j]["data"]
                subset_grouped = subset.groupby(self._analysis_config["x"])
                if "avg" in self._analysis_config and self._analysis_config["avg"] is not None:
                    x = list(subset_grouped.groups.keys())
                    y = subset_grouped[self._analysis_config["y"]].mean().tolist()
                else:
                    x = subset[self._analysis_config["x"]].tolist()
                    y = subset[self._analysis_config["y"]].tolist()
                
                if "sort" in self._analysis_config and self._analysis_config["sort"] is not None:
                    x, y = zip(*sorted(zip(x, y)))
                if "smooth" in self._analysis_config and self._analysis_config["smooth"] is not None:
                    x, y = smooth(x, y, self._analysis_config["smooth"])
                    
                
                if splt_len[1] > 1:
                    ax[splt_x,splt_y] = plot_by_type(ax[splt_x,splt_y], x, y, self._analysis_config["fig"]["type"], self._analysis_config["fig"]["kwargs"])
                    ax[splt_x,splt_y].set_title(data["plot"][i])
                    ax[splt_x,splt_y].legend(plt_legend)
                    
                    if "xlabel" in self._analysis_config["fig"]:
                        ax[splt_x,splt_y].set_xlabel(self._analysis_config["fig"]["xlabel"])
                    else:
                        ax[splt_x,splt_y].set_xlabel(self._analysis_config["x"])
                    if "ylabel" in self._analysis_config["fig"]:
                        ax[splt_x,splt_y].set_ylabel(self._analysis_config["fig"]["ylabel"])
                    else:
                        ax[splt_x,splt_y].set_ylabel(self._analysis_config["y"])
                        
                elif splt_len[0] > 1:
                    ax[splt_x] = plot_by_type(ax[splt_x], x, y, self._analysis_config["fig"]["type"], self._analysis_config["fig"]["kwargs"])
                    ax[splt_x].set_title(data["plot"][i])
                    ax[splt_x].legend(plt_legend)
                    
                    if "xlabel" in self._analysis_config["fig"]:
                        ax[splt_x].set_xlabel(self._analysis_config["fig"]["xlabel"])
                    else:
                        ax[splt_x].set_xlabel(self._analysis_config["x"])
                    if "ylabel" in self._analysis_config["fig"]:
                        ax[splt_x].set_ylabel(self._analysis_config["fig"]["ylabel"])
                    else:
                        ax[splt_x].set_ylabel(self._analysis_config["y"])
                        
                    splt_x += 1
                else:
                    ax = plot_by_type(ax, x, y, self._analysis_config["fig"]["type"], self._analysis_config["fig"]["kwargs"])
                    ax.set_title(data["plot"][i])
                    ax.legend(plt_legend)
                    
                    if "xlabel" in self._analysis_config["fig"]:
                        ax.set_xlabel(self._analysis_config["fig"]["xlabel"])
                    else:
                        ax.set_xlabel(self._analysis_config["x"])
                    if "ylabel" in self._analysis_config["fig"]:
                        ax.set_ylabel(self._analysis_config["fig"]["ylabel"])
                    else:
                        ax.set_ylabel(self._analysis_config["y"])
            if splt_len[0] > 1 and splt_y == splt_len[1]-1:
                splt_y = 0
                splt_x += 1
            elif splt_len[0] > 1:
                splt_y += 1
          
        if "figure_file" in self._analysis_config and self._analysis_config["figure_file"] is not None:
            #fig.tight_layout()
            fig.subplots_adjust(hspace=0.5, wspace=0.3)
            
            fig.savefig(self._analysis_config["figure_file"] + ".eps", format="eps", bbox_inches="tight", pad_inches=0)
            fig.savefig(self._analysis_config["figure_file"] + ".png", format="png", bbox_inches="tight", pad_inches=0.0)
            
            fig_data = { "fig_data": data, "fig": fig, "ax": ax }
            with open(self._analysis_config["figure_file"] + ".pkl", "wb") as f:
                pkl.dump(fig_data, f)
        
        if "render" in self._analysis_config and self._analysis_config["render"]:
            plt.show()
            while plt.fignum_exists(fignum):
                plt.pause(1)
        else:
            plt.close(fig)
                
        
            
            

def plot_by_type(ax, x, y, plot_type, plot_kwargs = None):
    """
    Plot data by type

    :param ax: (matplotlib.axes) Axes to plot on
    :param x: (list) x values
    :param y: (list) y values
    :param plot_type: (str) Type of plot
    :param plot_kwargs: (dict) Plot kwargs
    :return: (matplotlib.axes) Axes with plot
    """
    if plot_type == "line":
        ax.plot(x, y, **plot_kwargs)
    elif plot_type == "scatter":
        ax.scatter(x, y, **plot_kwargs)
    elif plot_type == "bar":
        ax.bar(x, y, **plot_kwargs)
    return ax

def smooth(x, y, smooth_factor):
    """
    Smooth data

    :param x: (list) x values
    :param y: (list) y values
    :param smooth_factor: (int) Number of points to smooth over
    :return: (tuple) Smoothed x and y values
    """
    x_smooth = []
    y_smooth = []
    for i in range(len(x)):
        if i < smooth_factor:
            x_smooth.append(x[i])
            y_smooth.append(np.mean(y[:i+1]))
        else:
            x_smooth.append(x[i])
            y_smooth.append(np.mean(y[i-smooth_factor:i+1]))
    return x_smooth, y_smooth
    
def bin_control(data : pd.DataFrame, control : str, bins : dict = {}):
    """
    Bin control variable data.

    :param data: (pd.DataFrame) Data to bin
    :param control: (str) Name of control variable
    :param bins: (dict) How to bin data
    :return: (list) List of dictionaries containing legend and data
    """
    if "bins" in bins and isinstance(bins["bins"], list):
        bin_vals = bins["bins"]
    elif "bins" in bins and isinstance(bins["bins"], int):
        bin_min = data[control].min()
        bin_max = data[control].max()
        bin_vals = np.linspace(bin_min, bin_max, bins["bins"]+1)
    elif "size" in bins:
        bin_vals = [data[control].min()]
        while bin_vals[-1] < data[control].max():
            bin_vals.append(bin_vals[-1] + bins["size"])
    else:
        bin_vals = list(data[control].unique())
    
    bin_names = []
    if "labels" in bins:
        bin_names = bins["labels"]
    
    control_bins = []
    if isinstance(bin_vals[0], str) or bins == {} or not bins["as_interval"]:
        for i in range(len(bin_vals)):
            bin_names.append(control + " " + str(bin_vals[i]))
            control_bins.append({"col":control, "op": "=", "val": bin_vals[i]}) 
    else:
        for i in range(len(bins)-1):
            if i == 0:
                bin_names.append(control + "[ " + str(bin_vals[i]) + ", " + str(bin_vals[i+1]) + "]")
                control_bins.append({"and": 
                    [{"col":control, "op": ">=", "val": bin_vals[i]}, 
                     {"col":control, "op": "=<", "val": bin_vals[i+1]}
                    ]})
            else:
                bin_names.append(control + "( " + str(bin_vals[i]) + ", " + str(bin_vals[i+1]) + "]")
                control_bins.append({"and": 
                    [{"col":control, "op": ">", "val": bin_vals[i]}, 
                     {"col":control, "op": "=<", "val": bin_vals[i+1]}
                    ]})
    return bin_names, control_bins

def package_data(data : dict, x : str, y : str, z : str = None):
    """
    Package data into a list of dictionaries containing x, y, and z data.

    :param data: (dict) Data to package
    :param x: (str) Name of x column
    :param y: (str) Name of y column
    :param z: (str) Name of z column
    :return: (list) List of dictionaries containing x, y, and z data
    """
    return {"legend": data["legend"], "x": data[x], "y": data[y], "z": data[z] if z is not None else None}
    
def merge_cols(data : pd.DataFrame, merge_cols : dict):
    """_
    Merge columns in a Pandas DataFrame (assumes values do not intersect).
    
    :param data: (pd.DataFrame) Data to merge columns in
    :param merge_cols: (dict) Dictionary mapping column names to columns to merge with
    :return: (pd.DataFrame) Data with columns merged
    """
    for el in merge_cols:
        data[el] = np.nan
        for i in range(len(data.index)):
            for col in merge_cols[el]:
                if data[col][i].notnull():
                    data[el][i] = data[col][i]
    return data

def filter_data(data : pd.DataFrame, filter_config : dict):
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
    if "logic" in filter_config and filter_config["logic"] is not None:
        return data[data_logic(data, filter_config["logic"])]
    return data

def data_logic(data : pd.DataFrame, logic_ops : dict):
    """
    Performs logical operations on columns
    
    :param data: (pd.DataFrame) Data to filter
    :param logic_ops: (dict) Dict of logical operations to perform
    :return: (pd.Series) Series of booleans indicating whether each row satisfies the conditions
    """
    if "and" in logic_ops:
        return logic_and(data, logic_ops["and"])
    elif "or" in logic_ops:
        return logic_or(data, logic_ops["or"])
    elif "col" in logic_ops:
        return logic_operation(data, logic_ops)
    else:
        raise ValueError("Invalid filter element")    

def logic_and(data : pd.DataFrame, conditions : list):
    """
    Filter a Pandas DataFrame based on specified values.
    
    :param data: (pd.DataFrame) Data to filter
    :param conditions: (dict) Filter configuration containing the following keys:
    :return: (pd.DataFrame) filtered data
    """
    logic_out = pd.Series([True]*len(data.index))
    if len(conditions) == 0:
        return logic_out
    for cond in conditions:
        logic_out = logic_out & data_logic(data, cond)
    return logic_out

def logic_or(data : pd.DataFrame,conditions : list):
    """
    Filter a Pandas DataFrame based on specified values.
    
    :param data: (pd.DataFrame) Data to filter
    :paramconditions: (dict) Filter configuration containing the following keys:
    :return: (pd.DataFrame) filtered data
    """
    if len(conditions) == 0:
        return pd.Series([True]*len(data.index))
    logic_out = pd.Series([False]*len(data.index))
    for cond in conditions:
        logic_out = logic_out | data_logic(data, cond)
    return logic_out

def logic_operation(data : pd.DataFrame, condition : dict):
    """
    Evaluate a condition on a Pandas DataFrame.

    :param data: (pd.DataFrame) Data to evaluate condition on
    :param condition: (dict) Condition to evaluate
    :return: (pd.Series) Series of booleans indicating whether each row satisfies the condition
    """
    
    if "col" not in condition:
        raise ValueError("Must provide column to evaluate condition on")
    if "op" not in condition:
        raise ValueError("Must provide operation to evaluate condition")
    if "val" not in condition:
        raise ValueError("Must provide value to evaluate condition")
    col = condition["col"]
    op = condition["op"]
    val = condition["val"]
    if op == "=":
        return data[col] == val
    elif op == "!=":
        return data[col] != val
    elif op == "<":
        return data[col] < val
    elif op == ">":
        return data[col] > val
    elif op == "<=":
        return data[col] <= val
    elif op == ">=":
        return data[col] >= val
    elif op == "in":
        if not isinstance(val, list):
            val = [val]
        return data[col].isin(val)
    elif op == "nin":
        if not isinstance(val, list):
            val = [val]
        return ~data[col].isin(val)
    else:
        raise ValueError("Invalid operation")
    
def include_cols_filter(data : pd.DataFrame, include_cols : list):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param include_cols: (list) List of columns to include
    :return: (pd.DataFrame) filtered data
    """
    return data[include_cols]

def exclude_cols_filter(data : pd.DataFrame, exclude_cols : list):
    """
    Filter a Pandas DataFrame based on specified values.

    :param data: (pd.DataFrame) Data to filter
    :param exclude_cols: (list) List of columns to exclude
    :return: (pd.DataFrame) filtered data
    """
    return data.drop(exclude_cols, axis=1)