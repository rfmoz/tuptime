#!/bin/bash


# This script update the tuptime database format from version 3.0.00 to 3.1.00

# Change the db origin:
# 	btime integer, uptime real, offbtime integer, endst integer, downtime real
# to:
# 	btime integer, uptime real, offbtime integer, endst integer, downtime real, kernel text

SOURCE_DB='/var/lib/tuptime/tuptime.db'

# Check bash execution
if [ ! -n "$BASH" ]; then
	echo "--- WARNING - execute only with BASH ---"
fi

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
	exit 3
fi

TMP_DB=$(mktemp)  # For temporary process db

cp "${SOURCE_DB}" "${TMP_DB}" || exit 4

# Adding new column
sqlite3 "${TMP_DB}" "ALTER TABLE tuptime RENAME TO tuptime_old;" && \
sqlite3 "${TMP_DB}" "CREATE TABLE tuptime (btime INT, uptime REAL, offbtime INT, endst INT, downtime REAL, kernel TEXT);" && \
sqlite3 "${TMP_DB}" "INSERT INTO tuptime(btime, uptime, offbtime, endst, downtime, kernel) SELECT btime, uptime, offbtime, endst, downtime, '' FROM tuptime_old;" && \
sqlite3 "${TMP_DB}" "DROP TABLE tuptime_old;" || exit 5

## Adding values for new columns downtime and offbtime
#ROWS=`sqlite3 "${TMP_DB}" "select max(oid) from tuptime;"`
#
#for I in $(seq 1 ${ROWS}); do
#	KERNEL='Linux-3.16.0-4-amd64-x86_64-with-debian-8.0'
#	sqlite3 "${TMP_DB}" "UPDATE tuptime SET kernel = \'${KERNEL}\' where oid = ${I}"
#done

# Backup old db and restore the new
mv "${SOURCE_DB}" "${SOURCE_DB}".back && \
mv "${TMP_DB}" "${SOURCE_DB}" && \
chmod 644 "${SOURCE_DB}" || exit 6
echo "Backup file in: ${SOURCE_DB}.back"

rm -f "${TMP_DB}"

echo "Process completed OK"
