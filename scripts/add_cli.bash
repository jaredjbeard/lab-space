#!/bin/bash

parent=$(dirname $(dirname $(realpath $0)))

if ! test -d "bin/"; then
    mkdir bin
fi

chmod +x lab_space/labspace.py

save_loc=bin/labspace
if test -f "$save_loc"; then
    rm "$save_loc"
fi
ln -s ../lab_space/labspace.py $save_loc
    
export_path='export PATH="$PATH:parent/bin/"'
export_path=${export_path/parent/$parent}
echo $export_path >> ~/.bashrc
source ~/.bashrc

if command -v python
then 
    python $parent/scripts/setup_core.py
else
    python3 $parent/scripts/setup_core.py
fi

echo "Lab Space CLI added!"
