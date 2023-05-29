#!/bin/bash

echo "Start: $(date)"
./compile.sh
rm -rf tmp
mkdir tmp

python3 test_plot_anim.py &
echo "======================================================"
echo "Plot PID $(ps aux | grep test_plot_anim | head -n 1 | cut -f 4 -d ' ')"
echo "======================================================"
SECONDS=0
./robot_control
echo "Elapsed: $SECONDS s"
echo "Recorded output: $(cat tmp/mn_ll | wc -l)/1000"
