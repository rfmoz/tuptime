#!/bin/bash


# This script update the tuptime database format from version 3.1.0 or above to to 4.0.0
#
# Usage:
#      Execute this script.
#      It will update the db file on /var/lib/tuptime/tuptime.db
#      The original db file will be renamed to /var/lib/tuptime/tuptime.[date].back
#
# Change the db origin:
#      btime integer, uptime real, offbtime integer, endst integer, downtime real, kernel text
# to:
#      btime integer, uptime real, rntime real, slptime real, offbtime integer, endst integer, downtime real, kernel text

SOURCE_DB='/var/lib/tuptime/tuptime.db'
USER_DB=$(stat -c '%U' "${SOURCE_DB}")
TMP_DBF=$(mktemp)
BKP_DATE=$(date +%s)

# Test file permissions
if [ -w "${SOURCE_DB}" ]; then
   echo -e "\n## Migrating tuptime database format ##\n"
   echo "Source file: ${SOURCE_DB}"
else
   echo "Please, execute this script with a privileged user that can write in: ${SOURCE_DB}"
   exit 1
fi

# Test sqlite3 command
sqlite3 -version > /dev/null
if [ $? -ne 0 ]; then
	echo "Please, install \"sqlite3\" command for manage sqlite v3 databases."
        exit 2
fi

# Work with a db copy
cp "${SOURCE_DB}" "${TMP_DBF}" || exit 4

# Adding new columns
sqlite3 "${TMP_DBF}" "CREATE TABLE tuptimeNew (btime integer, uptime integer, rntime integer, slptime integer, offbtime integer, endst integer, downtime integer, kernel text);" && \
sqlite3 "${TMP_DBF}" "UPDATE tuptime SET offbtime = cast(round(offbtime) as int);" && \
sqlite3 "${TMP_DBF}" "UPDATE tuptime SET uptime = cast(round(uptime) as int);" && \
sqlite3 "${TMP_DBF}" "UPDATE tuptime SET downtime = cast(round(downtime) as int);" && \
sqlite3 "${TMP_DBF}" "INSERT INTO tuptimeNew(btime, uptime, offbtime, endst, downtime, kernel) SELECT btime, uptime, offbtime, endst, downtime, kernel FROM tuptime;" && \
sqlite3 "${TMP_DBF}" "UPDATE tuptimeNew SET rntime = uptime;" && \
sqlite3 "${TMP_DBF}" "UPDATE tuptimeNew SET slptime = 0;" && \
sqlite3 "${TMP_DBF}" "DROP TABLE tuptime;" && \
sqlite3 "${TMP_DBF}" "ALTER TABLE tuptimeNew RENAME TO tuptime;" || exit 5

# Backup original db and rename the temp db as source
mv "${SOURCE_DB}" "${SOURCE_DB}"."${BKP_DATE}".back && \
mv "${TMP_DBF}" "${SOURCE_DB}" || exit 6
echo "Backup file: ${SOURCE_DB}.${BKP_DATE}.back"

# Set permission and user
chmod 644 "${SOURCE_DB}" && \
chown "${USER_DB}" "${SOURCE_DB}" || exit 7

echo "Process completed: OK"
