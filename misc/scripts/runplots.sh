#!/bin/bash


# This script executes all the plots available at the same time
# with the same arguments.

# Python command
PyEx='python3'

# Days ago
Past=30

# Set wide and height for fit all plots together on the screen
xrandr -v > /dev/null 2>&1
if [ $? -eq 0 ]; then
	Xrdr=`xrandr | grep -i ' connected\( primary\)\?'`  # Connected primary monitor
	Xmm=`echo $Xrdr | grep -o -P '(?<=\)\ ).*(?=mm\ x\ )'`  # X mm size number
	Ymm=`echo $Xrdr | grep -o -P '(?<=mm\ x\ ).*(?=mm)'`  # Y mm size number
	Xcm=`echo "$Xmm / 10 / 2 - 2" | bc`  # Half in cm minus boundary
	Ycm=`echo "$Ymm / 10 / 2 - 3" | bc`  # Half in cm minus boundary
else
	echo "### Install 'xrandr' for auto size based on monitor ###"
	Xcm=22
	Ycm=10
fi

echo -e "Days:\t$Past"
echo -e "Wide:\t$Xcm"
echo -e "Height:\t$Ycm"

echo -e "\nMaking 4 plots in backgroud...\n"
XnY="-W $Xcm -H $Ycm"
$PyEx ./tuptime-plot1.py $XnY -p $Past > /dev/null &
$PyEx ./tuptime-plot1.py $XnY -p $Past -x > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -p $Past > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -p $Past -x
