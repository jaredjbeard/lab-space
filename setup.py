#!/usr/bin/python
from setuptools import setup
import os

current = os.path.dirname(os.path.realpath(__file__))

# setup(
#     name="experimentlab",
#     version="0.0.1",
#     install_requires=["nestifydict",
#                       "reconfigurator"],
# )

# import reconfigurator as rc
import nestifydict as nd
import json

with open(current + "/experimentlab/config/core/core_default.json", "rb") as f:
    core_default = json.load(f)
    
defaults = { "path": current + "/experimentlab/config/"}

defaults = nd.merge(core_default, defaults)

with open(current + "/experimentlab/config/core/config.json", "w+") as f:
    json.dump(defaults,f, indent=4)



