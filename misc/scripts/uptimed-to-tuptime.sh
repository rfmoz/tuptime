#!/bin/bash

# This script migrate the uprecords registers to tuptime db
#
# Note the following:
#   Uptimed is an uptime record daemon keeping track of the highest uptimes that a computer system ever had.
#   Tuptime is a tool for report the historical and statistical real time of the system, keeping it between restarts.
#
# If you used Uptimed for the purpose of Tuptime, wich is possible changing some variables (for example, normally Uptimed 
# keep only last 50 max uptimes), this script can convert the register values to Tuptime format.
# For achieve that:
#	1- Uptimed must be running and Tuptime installed.
#	2- Execute this script and accept replace database if the values are ok. Previous Tuptime values will be lost.
#	3- Done.
# Normaly the kernel name is not exactly the same, it is possible to correct it directly into Tuptime db sqlite3.

SOURCE_F='/var/spool/uptimed/records'
DEST_F='/var/lib/tuptime/tuptime.db'

echo '- Uprecors to Tuptime migrate script'
echo ''

# Test file permissions
if [ -r "${SOURCE_F}" ]; then
   echo "Migrating from: ${SOURCE_F}"
else
   echo "Please, execute this script with a privileged user that can read in: ${SOURCE_F}"
   exit 1
fi
if [ -w "${DEST_F}" ]; then
   echo "To: ${DEST_F}"
else
   echo "Please, execute this script with a privileged user that can write in: ${DEST_F}"
   exit 1
fi
echo ''
while true; do
    read -p "Correct? (y/n)" yn
    case ${yn} in
        [Yy]* ) break;;
        [Nn]* ) echo 'Please, modify SOURCE_F or DEST_F in the header of the script with the right location'; exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# Test sqlite3 command
sqlite3 -version > /dev/null
if [ $? -ne 0 ]; then
        echo "Please, install "sqlite3" command for manage sqlite v3 databases."
        exit 2
fi

# Test bc command
bc -version > /dev/null
if [ $? -ne 0 ]; then
        echo "Please, install "bc" command."
        exit 2
fi

TMP_F=`mktemp`  # For ordered uprecords values
TMP_F2=`mktemp`  # For backup Tuptime db file
TMP_FDB=`mktemp`  # For temporary tuptime db
echo 'Ordering Uprecors registers by btime...'
cat ${SOURCE_F} | sort -k2 -t\: > ${TMP_F}
LINES_S_F=`wc -l ${TMP_F} | awk '{print $1}'`

# Create database
sqlite3 ${TMP_FDB} "CREATE TABLE tuptime (btime INT, uptime REAL, offbtime INT, endst INT, downtime REAL, kernel TEXT);"

# For each line in the file
for I in $(seq 1 ${LINES_S_F}); do
	L_ACT=`cat ${TMP_F} | sed -n ${I}p`  # Actual line

	UPTIME=`echo ${L_ACT} | cut -d: -f1`
	BTIME=`echo ${L_ACT} | cut -d: -f2`
	KERNEL=`echo ${L_ACT} | cut -d: -f3`
	OFFBTIME=$(echo ${UPTIME} + ${BTIME} | bc)
	ENDST='1'

	# Following line needed for calculate downtime
	if [ $I -ne ${LINES_S_F} ]; then
		Z=$((I+1))
		L_NEXT=`cat ${TMP_F} | sed -n ${Z}p`  # Following line

		BTIME_NEXT=`echo ${L_NEXT} | cut -d: -f2`
		DOWNTIME=$(echo ${BTIME_NEXT} - ${OFFBTIME} | bc)
	else
		DOWNTIME='-1'
	fi

	echo "Processing line ${I}: " ${L_ACT}
	echo 'btime:' ${BTIME}
	echo 'uptime:' ${UPTIME}
	echo 'offbtime:' ${OFFBTIME}
	echo 'endst:' ${ENDST}
	echo 'downtime:' ${DOWNTIME}
	echo 'kernel:' ${KERNEL}
	echo ''

	sqlite3 ${TMP_FDB} "INSERT INTO tuptime values (${BTIME}, ${UPTIME}, ${OFFBTIME}, ${ENDST}, ${DOWNTIME}, "\'"${KERNEL}"\'")"

done

tuptime -tf ${TMP_FDB}

echo ''
while true; do
    read -p "Do you want to replace the entire Tuptime database with this values? Are they correct? (y/n)" yn
    case ${yn} in
        [Yy]* ) echo "Creating backup of ${DEST_F} in ${TMP_F2}"
		cp ${DEST_F} ${TMP_F2}
		echo "Replacing ${DEST_F}"
		cp ${TMP_FDB}  ${DEST_F}
		echo 'Done'
		break;;
        [Nn]* ) echo 'Exit without doing nothing.'
		break;;
        * ) echo "Please answer yes or no.";;
    esac
done

rm -f ${TMP_F}
rm -f ${TMP_FDB}
