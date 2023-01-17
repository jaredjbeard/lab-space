====================
Run Experiment Guide
====================

Run experiment is the primary interface for running standalone testing and data collection of decision making tools. 
It provides support for multithreaded data collection, sampling variables, interfaces with Gym standards (OpenAI and soon Isaac).

Running an experiment:

```
python3 run_expt.py <alg config file name> <env config file name> <opt: # trials> <opt: # threads> <opt: log level> <opt: save file name> <opt: clear save file>
```

- The default config file path is `config/<alg, env>/<file>.json`.

- The default save file path is `analysis/data/<file>.json`

For more information on configuations, please see :ref:`configuration docs <config>`.

Notes
#####

- When running multiple threads or trials, rendering will be ignored to prevent errors. 