
from importlib.resources import path
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import argparse

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Lab Space CLI')
    parser.add_argument('-r',   '--run',           action="store_const", const=True,  help='Runs algorithm, if unspecified runs user default')
  
    args = parser.parse_args()
    print(args.run)
    # if args.run:
        # parser.add_argument('-c',   '--config',        type=str,   help='Configuration file to use')

        # args = parser.parse_args()