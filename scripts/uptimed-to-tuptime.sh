#!/bin/bash

# This script migrate the uprecords registers to tuptime db
#
# Note the following:
#   Uptimed is an uptime record daemon keeping track of the highest uptimes a computer system ever had.
#   Tuptime is a tool for report the historical and statistical running time of the system, keeping it between restarts.
#
# If you used Uptimed for the purpose of Tuptime, wich is possible changing some variables (for example, usually uptimed 
# keep only last 50 max uptimes), this script can convert the register values to Tuptime format.
# For achieve that:
#	1- Uptimed must be running
#	2- Execute this script and replace generated database file. Previous Tuptime values will be lost.
#	3- Check that tuptime runs ok with the values
#	4- Stop Uptimed
# Usually the kernel name are not the same, correct it with...

SOURCE_F='/var/spool/uptimed/records'
TMP_F=`mktemp`  # For ordered uprecords values
TMP_FDB=`mktemp`  # For temporary tuptime db
cat $SOURCE_F | sort -k2 -t\: > $TMP_F
LINES_S_F=`wc -l ${TMP_F} | awk '{print $1}'`

# Create database
sqlite3 ${TMP_FDB} "CREATE TABLE tuptime (btime INT, uptime REAL, offbtime INT, endst INT, downtime REAL, kernel TEXT);"

# For each line in the file
for I in $(seq 1 ${LINES_S_F}); do
	L_ACT=`cat $TMP_F | sed -n ${I}p`  # Actual line

	UPTIME=`echo $L_ACT | cut -d: -f1`
	BTIME=`echo $L_ACT | cut -d: -f2`
	KERNEL=`echo $L_ACT | cut -d: -f3`
	OFFBTIME=$(echo ${UPTIME} + ${BTIME} | bc)
	ENDST='1'

	# Following line needed for calculate downtime
	if [ $I -ne ${LINES_S_F} ]; then
		Z=$((I+1))
		L_NEXT=`cat $TMP_F | sed -n ${Z}p`  # Following line

		BTIME_NEXT=`echo $L_NEXT | cut -d: -f2`
		DOWNTIME=$(echo ${BTIME_NEXT} - ${OFFBTIME} | bc)
	else
		DOWNTIME='-1'
	fi

	echo "Processing line $I: " $L_ACT
	echo 'btime:' $BTIME
	echo 'uptime:' $UPTIME
	echo 'offbtime:' $OFFBTIME
	echo 'endst:' $ENDST
	echo 'downtime:' $DOWNTIME
	echo 'kernel:' $KERNEL
	echo ''

	sqlite3 ${TMP_FDB} "INSERT INTO tuptime values (${BTIME}, ${UPTIME}, ${OFFBTIME}, ${ENDST}, ${DOWNTIME}, "\'"${KERNEL}"\'")"

done

tuptime -tf $TMP_FDB

while true; do
    read -p "Do you want to replace the original database? Are the previous values correct? (y/n)" yn
    case $yn in
        [Yy]* ) echo "copiar"; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done


rm -f $TMP_F
rm -f $TMP_FDB
