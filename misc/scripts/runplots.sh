#!/bin/bash


# This script executes all the plots available at the same time
# with the same arguments.

# Python command
PYEX='python3'

# Days ago
past=30

# Size wide and height for nice display on a 16:9 screen
height=10
wide=22

echo "Making plots in backgroud..."
$PYEX ./tuptime-plot1.py -W $wide -H $height -p $past > /dev/null &
$PYEX ./tuptime-plot1.py -W $wide -H $height -p $past -x > /dev/null &
$PYEX ./tuptime-plot2.py -W $wide -H $height -p $past > /dev/null &
$PYEX ./tuptime-plot2.py -W $wide -H $height -p $past -x > /dev/null &
