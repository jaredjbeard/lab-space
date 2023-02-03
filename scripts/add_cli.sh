#!/bin/bash

parent=$(dirname $(dirname $(realpath $0)))

mkdir bin

chmod +x lab_space/labspace.py
ln -s ../lab_space/labspace.py bin/labspace
    
export_path='export PATH="$PATH:parent/../bin/"'
export_path=${export_path/parent/$parent}
echo $export_path >> ~/.bashrc
source ~/.bashrc

python setup_core.py

echo "Lab Space CLI added!"
