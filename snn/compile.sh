#!/bin/bash

mkdir -p build
cd build
cmake ../ && make
if [ $? -eq 0 ];
then
    cp main_serial ../robot_control
    echo "Compile Complete"
else
    exit $?
fi