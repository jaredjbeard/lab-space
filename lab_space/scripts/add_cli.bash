#!/bin/bash

parent=$(dirname $(dirname $(realpath $0)))

if ! test -d "bin/"; then
    mkdir bin
fi

chmod +x labspace.py

save_loc=bin/labspace
if test -f "$save_loc"; then
    rm "$save_loc"
fi
ln -s ../labspace.py $save_loc
    
export_path='export PATH="$PATH:parent/bin/"'
export_path=${export_path/parent/$parent}

if command -v python
then 
    echo "Initializing Core to Python"
    python $parent/scripts/setup_core.py
else
    echo "Initializing Core to Python3"
    python3 $parent/scripts/setup_core.py
fi

if grep -Fxq "$export_path" ~/.bashrc; then
    echo "Lab Space CLI Updated!"
    exit 0
else
    echo $export_path >> ~/.bashrc
    source ~/.bashrc
fi

echo "Lab Space CLI added!"
