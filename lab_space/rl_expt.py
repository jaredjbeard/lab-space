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