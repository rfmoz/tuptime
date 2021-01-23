#!/bin/bash


# This script executes all the plots available at the same time
# with the same arguments.

# Defaults
PyEx='python3'
Size='22x10'
pDays='30'
EndDT=$(date +"%d-%m-%y")

while getopts s:p:e: flag; do
    case "${flag}" in
        s)
	  Size=$(grep -oP '\d+x\d+' <<< ${OPTARG})
	;;
        p)
	  pDays=$(grep -oP '\d+' <<< ${OPTARG})
	;;
        e)
	  EndDT=$(grep -oP '\d+-\w+-\d+' <<< ${OPTARG})
	;;
	*)
	  echo "ERROR: Invalid argument flag" && exit -1
	;;
    esac
done

# Set X and Y size
Xcm=$(cut -dx -f1 <<< $Size)
Ycm=$(cut -dx -f2 <<< $Size)	
XnY="-W $Xcm -H $Ycm"

echo "Execution: $0 [-s Width x Height] [ -p Past Days] [ -e End Date]"
echo "Example:   $0 -s 22x10 -d 30 -e 31-Dec-20"
echo ""

echo -e "Making 4 plots in background...\n"
echo -e "Wide x Height:\t ${Xcm}x${Ycm}"
echo -e "Past Days:\t ${pDays}"
echo -e "End Date:\t ${EndDT}\n"

$PyEx ./tuptime-plot1.py $XnY -e $EndDT -p $pDays > /dev/null &
$PyEx ./tuptime-plot1.py $XnY -e $EndDT -p $pDays -x > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -e $EndDT -p $pDays > /dev/null &
$PyEx ./tuptime-plot2.py $XnY -e $EndDT -p $pDays -x
