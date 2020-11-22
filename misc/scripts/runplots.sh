#!/bin/bash


# This script executes all the plots available at the same time
# with the same arguments.

# Python command
PyEx='python3'

# X and Y wide and height for fit all plots together on the screen
if [ -z "$1" ]; then
	XargY='22x10'
else
	XargY=`grep -oP '\d+x\d+' <<<$1`
fi
Xcm=`cut -dx -f1 <<< $XargY`
Ycm=`cut -dx -f2 <<< $XargY`

# Days ago
if [ -z "$2" ]; then
	Past='30'
else
	Past=`grep -oP '\d+' <<<$2`
fi
echo "Execution: $0 [Width x Height] [Past Days]"
echo "Example:   $0 22x10 30"
echo ""
if [ -z "$XargY" ] || [ -z "$Past" ]; then exit; fi

echo -e "Days:\t$Past"
echo -e "Wide:\t$Xcm"
echo -e "Height:\t$Ycm"

echo -e "\nMaking 4 plots in backgroud...\n"
XnY="-W $Xcm -H $Ycm"
$PyEx ./tuptime-plot1.py $XnY -p $Past > /dev/null &
$PyEx ./tuptime-plot1.py $XnY -p $Past -x > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -p $Past > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -p $Past -x
