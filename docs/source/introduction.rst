=========================
Introduction to Lab Space
=========================

Lab Space streamlines data collection and post-processing in experiments through its experiment manager. Simply define a function and reference parameters, and the backend takes care of saving, multiprocessing, and more. With our CLI, you can run experiments from the command line, even on remote servers or clusters. In the future, a data processing pipeline will allow for easy generation and export of plots from your data.


Experiments
###########

The experiment class provides your interface for running experiments. Simply pass the following and we will handle the rest:
- a list of dictionaries (or `Reconfigurator File <https://reconfigurator.readthedocs.io/en/latest/markup.html>`_ ) with the parameters for each trial
- a dictionary of experimental parameters (a reference to your experiment function, number of trials, number of processes, where/if to save, and how many repetitions)
- a logging setting 

These can be passed on initialization or at runtime, if your trials are generated dynamically or from feedback.

Checkout the :doc:`API <../lab_space>` for more info.

Lab Space CLI
##################

Lab Space comes with a CLI for running experiments from the command line. This allows you to run experiments on remote servers or clusters. The CLI can be accessed using `labspace <flag> <args>`. Use `man lab_space` for more information.

The key features of the CLI include the ability to register functions as strings so you can call them from the command line, the ability to set up workspaces to host experimental configurations, the ability to update and save experiment parameters

To run an experiment, you can simply use the '-r' flag if your experiment is ready to go.

Experiment Registration
***********************

To register an exeriment, you have two options
- `labspace -er <module_path> <module_name> <function_key> <function_name>` for packages which are not installed
- `labspace -er <module_name> <function_key> <function_name>` for packages which are installed

As an example, if I have a test file called `test.py` with a function called `test_func` in the `test` package, I can register it using `labspace -er /home/<user>/test/test.py test_func1 test_func`. I can then run it using `labspace -r -e test_func1`.

Workspace Setup
***************

To set up my workspace, I can set default paths and files for my trial configurations, and experiments. I can also set my default save path.
The flags are as follows:
- -cp : configure path
- -ctp : configure trial path
- -ct : configure trial file
- -cep : configure experiment path
- -ce : configure experiment file
- -csp : configure save path

Experiment Setup
****************

To modify I an experiment I can use the following flags:
- -tt : number of trials
- -tp : number of processes
- -ts : save file
- -tcs : clear save (use a 1 for true, 0 for false)
- -tl : log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- -tc : compile a reconfigurator based config

Then these parameters can be saved using 
- -s : save both
- -se : save experiment (specifiy a file name or use none to save to current file)
- -st : save trial (specifiy a file name or use none to save to current file)
- -p : print


Adding CLI
**********

To add Lab Space command line interface in Linux, navigate to `/home/<user>/.local/lib/python<version#>/site-packages/lab-space/`.
Then run `bash scripts/add_cli.bash`. This will add the reconfigurator CLI to your path. (in the future we may seek to add this at install time).

The reconfigurator can be accessed using `labspace <flag> <args>`. Use `man labspace` for more information.
