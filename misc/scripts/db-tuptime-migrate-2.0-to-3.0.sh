#!/bin/bash


# This script update the tuptime database format from versions previous 3.0.00

# Change the db origin:
#      uptime real, btime integer, shutdown integer
# to:
#      btime integer, uptime real, offbtime integer, endst integer, downtime real

SOURCE_DB='/var/lib/tuptime/tuptime.db'

# Test file permissions
if [ -w "${SOURCE_DB}" ]; then
   echo "Migrating tuptime database format"
else
   echo "Please, execute this script with a privileged user that can write in: ${SOURCE_DB}"
   exit 1
fi

# Test sqlite3 command
sqlite3 -version > /dev/null
if [ $? -ne 0 ]; then
	echo "Please, install \"sqlite3\" command for manage sqlite v3 databases"
        exit 2
fi

# Test bc command
bc -version > /dev/null
if [ $? -ne 0 ]; then
        echo "Please, install \"bc\" command"
        exit 2
fi

TMP_DB=$(mktemp)  # For temporary process db

cp "${SOURCE_DB}" "${TMP_DB}"

# Check db format
sqlite3 "${TMP_DB}" "PRAGMA table_info(tuptime);" | grep -E 'end_state|downtime|offbtime' > /dev/null 
if [ $? -eq 0 ]; then
	echo "Database is already in new format"
        exit 3
fi

# Change shutdown column to end_state
sqlite3 "${TMP_DB}" "ALTER TABLE tuptime RENAME TO tuptime_old;"
sqlite3 "${TMP_DB}" "CREATE TABLE tuptime (uptime REAL, btime INT, endst INT, downtime REAL, offbtime INT);"
sqlite3 "${TMP_DB}" "INSERT INTO tuptime(uptime, btime, endst) SELECT uptime, btime, shutdown FROM tuptime_old;"
sqlite3 "${TMP_DB}" "DROP TABLE tuptime_old;"

# Adding values for new columns downtime and offbtime
ROWS=$(sqlite3 "${TMP_DB}" "select max(oid) from tuptime;")

for I in $(seq 1 "${ROWS}"); do
	UPTIME=$(sqlite3 "${TMP_DB}" "SELECT uptime from tuptime where oid = ${I};")
	BTIME=$(sqlite3 "${TMP_DB}" "SELECT btime from tuptime where oid = ${I};")
        Z=$((I+1))
	NEXT_BTIME=$(sqlite3 "${TMP_DB}" "SELECT btime from tuptime where oid = ${Z};")

	OFFBTIME=$(echo "${UPTIME}" + "${BTIME}" | bc)
	DOWNBTIME=$(echo "${NEXT_BTIME}" - "${OFFBTIME}" | bc)

	sqlite3 "${TMP_DB}" "UPDATE tuptime SET downtime = ${DOWNBTIME}, offbtime = ${OFFBTIME} where oid = ${I}"
	
done

# Clear last row shutdown values
sqlite3 "${TMP_DB}" "UPDATE tuptime SET downtime = '-1', offbtime = '-1' where oid = ${I}" 

# Order columns
sqlite3 "${TMP_DB}" "ALTER TABLE tuptime RENAME TO tuptime_old;"
sqlite3 "${TMP_DB}" "CREATE TABLE tuptime (btime INT, uptime REAL, offbtime INT, endst INT, downtime REAL);"
sqlite3 "${TMP_DB}" "INSERT INTO tuptime(btime, uptime, offbtime, endst, downtime) SELECT btime, uptime, offbtime, endst, downtime FROM tuptime_old;"
sqlite3 "${TMP_DB}" "DROP TABLE tuptime_old;"

# Adding new column
sqlite3 "${TMP_DB}" "ALTER TABLE tuptime RENAME TO tuptime_old;"
sqlite3 "${TMP_DB}" "CREATE TABLE tuptime (btime INT, uptime REAL, offbtime INT, endst INT, downtime REAL, kernel TEXT);"
sqlite3 "${TMP_DB}" "INSERT INTO tuptime(btime, uptime, offbtime, endst, downtime, kernel) SELECT btime, uptime, offbtime, endst, downtime, '' FROM tuptime_old;"
sqlite3 "${TMP_DB}" "DROP TABLE tuptime_old;"

# Backup old db and restore the new
mv "${SOURCE_DB}" "${SOURCE_DB}".back
mv "${TMP_DB}" "${SOURCE_DB}"
chmod 644 "${SOURCE_DB}"

rm -f "${TMP_DB}"

echo "Backup file in: ${SOURCE_DB}.back"
echo "Process completed OK"

