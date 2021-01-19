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

# End Date
if [ -z "$3" ]; then
	EndDate=''
else
	EndDate="-e `grep -oP '\d+-\w+-\d+' <<<$3`"
fi

echo "Execution: $0 [Width x Height] [Past Days] [End Date]"
echo "Example:   $0 22x10 30 31-Dec-20"
echo ""
if [ -z "$XargY" ] || [ -z "$Past" ]; then exit; fi

echo -e "Making 4 plots in background...\n"
echo -e "Wide x Height:\t${Xcm}x${Ycm}"
XnY="-W $Xcm -H $Ycm"
$PyEx ./tuptime-plot1.py $XnY $EndDate -p $Past > /dev/null &
$PyEx ./tuptime-plot1.py $XnY $EndDate -p $Past -x > /dev/null &
$PyEx ./tuptime-plot2.py $XnY $EndDate -p $Past > /dev/null &
$PyEx ./tuptime-plot2.py $XnY $EndDate -p $Past -x
