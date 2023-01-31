#!/usr/bin/python
"""
This script is intended to run single or multithreaded decision making experiments
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

from abc import ABC,abstractmethod
from multiprocessing import Pool, Lock
import logging
import itertools
import numpy as np
from copy import deepcopy
import pickle

import nestifydict as nd
import reconfigurator as rc

class Experiment():
    """
    Performs experimental trials for a given algorithm and gym environment
    
    *If using sample_expt, remember that this will affect `n_trials`. Depending on how an experiment is defined,
    this could lead to double counting and an explosion in simulations.* 
    If both are being used, it is recommented to set n_trials to no more than 5 unless 
    a deep investigation into a given state is needed.
    
    :param alg_file: (str) Filename for algorithm params (see :doc:`config/core/get_defaults.py` for default path and :ref:`Config <config>` for specification)
    :param env_file: (str) Filename for env params (see :doc:`config/core/get_defaults.py` for default path and :ref:`Config <config>` for specification)
    :param core_file: (str) Filename for system params (such as file paths (see :doc:`config/operational.json` for defaults and :ref:`Update Config <update_config>` for command tools))
    :param n_trials: (int) Number of trials to run for each set of parameters, *default*: 1
    :param n_threads: (int) Number of threads to use, *default*: 1
    :param log_level: (str) Log level (does not override default values), *default*: WARNING
    :param file_name: (str) file to save data (default path is "~/data/"), if none does not save, *default*: None
    :param clear_save: (bool) clears data from pickle before running experiment, *default*: False
    """
    def __init__(self, alg_file : str, env_file : str, core_file: str, n_trials : int = 1, n_threads : int = 1, log_level : str = "WARNING", file_name : str = None, clear_save : bool = False):
        
        super(Experiment, self).__init__()
        
        log_levels = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR ,"CRITICAL": logging.CRITICAL}
        self._log_level = log_levels[log_level]
                                             
        logging.basicConfig(stream=sys.stdout, format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=self._expt_config["log_level"])
        self._log = logging.getLogger(__name__)
        
        self._log.warn("RunExperiment Init, perform " + str(n_trials) + " trials across " + str(n_threads) + "threads")
        
        f = open(parent + "/config/alg/" + alg_file +  ".json")
        self._alg_config = json.load(f)
        f.close()
        self._alg_default = self._alg_config.pop('default', None)
        if "log_level" not in self._alg_default:
            self._alg_default["log_level"] = log_level
        self._log.warn("Accessed algorithm configuration")
        
        f = open(parent + "/config/env/" + env_file +  ".json")
        self._env_config = json.load(f)  
        f.close()
        self._env_default = self._env_config.pop('default', None)
        if "log_level" not in self._env_default:
            self._env_default["log_level"] = log_level
        self._log.warn("Accessed Environment configuration") 
        
        self._n_trials = n_trials
        self._n_threads = n_threads  
        
        if file_name is not None:
            self.__fp = os.path.dirname(__file__) + "/data/" + file_name + ".pkl"
            self._log.warn("Save path set to " + self.__fp)
            if clear_save:
                with open(self.__fp, 'wb') as f:
                    pickle.dump([],f)
        else:
            self.__fp = None
        
        self.__lock = lock = Lock() 
            
    def list_trials(self):
        """
        Generates a set of trials from the environment and algorithm params provided

        :return: (list(dict)) contains list of the parameters for each algorithm
        """
        
    
    def generator_trials(self):
        """
        Generator implementation for yielding a set of trials from the environment and algorithm params provided

        :return: (list(dict)) contains list of the parameters for each algorithm
        """
    
    def _start_pool(self, expts):
        """
        Starts Multithreading pool and performs series of experiments

        :param expts: (list([dict,dict])) List of experiments with parameters for (algorithm, environment)
        """
        self._log.warn("Starting pool")
        if self.__fp is not None:
            if os.path.exists(self.__fp):
                with open(self.__fp, "rb") as f:
                    data = pickle.load(f)
                    self._log.warn("Accessed database")
            else:   
                with open(self.__fp, 'wb') as f:
                    pickle.dump([],f)
                self._log.warn("Starting blank database")

        if self._n_threads > 1:
            self._log.warn("Starting multithread pool")        
            p = Pool(self._n_threads)
            p.map(self._simulate, expts)
        else:
            self._log.warn("Starting single thread pool")        
            for t in expts:
                self._simluate(t)
        
        self._log.warn("Pool closed, simulations complete")        

    def _simulate_save(self, params : dict):
        """
        Simulates and saves a single experimental trial
        
        :param params: (dict) Contains "alg" and "env" with corresponding params
        """
        self._log.debug("Simulation")
        env = gym.make(params["env"]["env"],max_episode_steps = params["env"]["max_time"], params=params["env"]["params"])
        s = env.reset()
        params["env"]["state"] = deepcopy(s)
        planner = get_agent(params["alg"]["params"],params["env"])

        done = False
        ts = 0
        accum_reward = 0

        while(not done):
            a = planner.evaluate(s, params["alg"]["search"])
            s, r,done, is_trunc, info = env.step(a)
            done = done or is_trunc
            ts += 1
            accum_reward += r

        self._log.debug("Simulation complete")
        if self.__fp is not None:
            with open(self.__fp, "rb") as f:
                data = pickle.load(f)
                self._log.warn("Accessed database")
            data.append(params)
            with open(self.__fp, "wb") as f:
                pickle.dump(data,f)
                self._log.warn("Saved to database")

    def _simulate(self, params : dict) -> dict:
        """
        Simulates and saves a single experimental trial
        
        :param params: (dict) Contains "alg" and "env" with corresponding params
        """
        self._log.debug("Simulation")
        env = gym.make(params["env"]["env"],max_episode_steps = params["env"]["max_time"], params=params["env"]["params"])
        s = env.reset()
        params["env"]["state"] = deepcopy(s)
        planner = get_agent(params["alg"]["params"],params["env"])

        done = False
        ts = 0
        accum_reward = 0

        while(not done):
            a = planner.evaluate(s, params["alg"]["search"])
            s, r,done, is_trunc, info = env.step(a)
            done = done or is_trunc
            ts += 1
            accum_reward += r

        self._log.debug("Simulation complete")
        return params
    
    def _simulate(self, params : dict):
        """
        Simulates and saves a single experimental trial
        
        :param params: (dict) Contains "alg" and "env" with corresponding params
        """
        self._log.debug("Simulation")
        env = gym.make(params["env"]["env"],max_episode_steps = params["env"]["max_time"], params=params["env"]["params"])
        s = env.reset()
        params["env"]["state"] = deepcopy(s)
        planner = get_agent(params["alg"]["params"],params["env"])
    
        done = False
        ts = 0
        accum_reward = 0

        while(not done):
            a = planner.evaluate(s, params["alg"]["search"])
            s, r,done, is_trunc, info = env.step(a)
            done = done or is_trunc
            ts += 1
            accum_reward += r
            if params["env"]["params"]["render"] != "none":
                env.render()
        
        if ts < params["env"]["max_time"]:
            accum_reward += (params["env"]["max_time"]-ts)*r
        
        if self.__fp is not None:
            data_point = nd.unstructure(params)
            data_point["time"] = ts
            data_point["r"] = accum_reward
            if "pose" in data_point and "goal" in data_point:
                data_point["distance"] = np.linalg.norm(np.asarray(data_point["pose"])-np.asarray(data_point["goal"]))
            data_point["final"] = deepcopy(s)
            if "pose" in s and "goal" in data_point:
                data_point["final_distance"] = np.linalg.norm(np.asarray(s["pose"])-np.asarray(data_point["goal"]))
    
            self.__lock.acquire()
            with open(self.__fp, "rb") as f:
                data = pickle.load(f)
            
            data.append(data_point)
            
            with open(params["fp"], 'wb') as f:
                pickle.dump(data,f)      
            
            self.__lock.release()

    def run(self):
        """
        Runs Experiment. This is the primary UI.
        """
        self._log.warn("Running experiments")
        expts = self._list_trials()
        self._start_pool(expts)
    
    def __expand_trials(self, d):
        """
        Unpacks a dictionary into a sequence of lists for trial generation
        
        :param d: (dict) params to expand
        :return: (list(dict)) trials
        """
        self._log.info("Expanding trials")
        
        if "alg" in d:
            temp = deepcopy(self._alg_default)
        elif "env" in d:
            if n_threads > 1:
                d["params"]["render"] = "none"
            temp = deepcopy(self._env_default)
        temp.pop("sample")
        
        # Because merge does not recurse into non dict types and
        # the whitelists are dependent on internal factors 
        # (e.g. we have a variable to override the default that is not configurable)
        # we may wish to exclude certain elements. This accomplished here
        if "whitelists" in temp:
            if "whitelists" in d:
                whitelists = d["whitelists"]
            else:
                whitelists = {}
                
            for key in temp["whitelists"]:
                temp = []
                for el in temp["whitelists"][key]:
                    if nd.find_key(d,el) == None:
                        temp.append(el)
                if temp != []:
                    if key not in d["whitelists"]:
                        whitelists[key] = temp
                    elif key in whitelists:
                        whitelists[key] += temp
                        np.unique(whitelists[key])
                
            if whitelists != {}:
                d["whitelists"] = whitelists
                
        d = nd.merge(temp, d)
        
        if "sample" in d:
            sampler.sample_all(d["sample"], d)
            d.pop("sample")
            
        if "whitelist" not in d:
            return [d]
        else:
            trials = []
            
            d.pop("whitelists")
            
            if "combo" in whitelists:
                d_flat = nd.unstructure(d)

                d_filter = {}
                for el in whitelists["combo"]:
                    d_filter[el] = d_flat[el]

                combos = list(itertools.product(*d_filter.values()))

                for el, i in enumerate(combos):
                    temp = dict(zip(deepcopy(d_filter.keys()), deepcopy(el)))
                    temp = nd.merge(d_flat,temp)
                    trials[i] = nd.structure(temp,d)

            return deepcopy(trials)
        
        
# "core default" is where things are initialized this includes file os.pathsep
# "config" in core contains the operating file path and settings for expt backend
# "default contains some default parameters for experimental config" Users are meant to replace this guy
"""
Main does the following
    - Loads the core config which has default file paths from install (to change this use reconfigurator or manually edit)
    - Loads config file for experiment as required parameter
    - if "-r" used, default config will be reset to initial config
"""
if __name__=='__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == "-r":
        rc.replace_file("/config/core/config.json", "/config/core/core_default.json")
        exit("Reset core")
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        with open("/core/core.json", "r+") as f:
            core_config = json.load(f)
            core_config["path"] = os.getcwd()
            exit("Current File Path updated to this directory")
    
    with open("/core/core.json", "rb") as f:
        core_config = json.load(f)
        
    if len(sys.argv) >= 1:
        i = 1;
        while i < len(sys.argv):
            if sys.argv[i] == "--trials":
                
                i += 2
            elif sys.argv[i] == "--threads":
                
                i += 2
            elif sys.argv[i] == "-c":
                
                i += 1
                
            elif sys.argv[i] == "--core-config":
                
                i += 2
            
            else:
                with open(core_config["path"] + sys.argv[i], "rb") as f:
                    expt_config = json.load(f)
                i += 1
                
    
        
    expts = RunExperiment(alg_config_file, core_config_file, n_trials, n_threads, clear_save)
    
    expts.run()

