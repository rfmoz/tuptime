#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Migrate Uptimed records to Tuptime"""

import os, sys, logging, sqlite3, argparse
from shutil import which, copyfile

# Script to migrate uptimed records to a sqlite file suitable to be
# used by tuptime.
# Adding records to an existing tuptime db is not supported.

# Copyright: gustavo panizzo <gfa@zumbi.com.ar> 2018-11-18
# License: GPL-2.0+
#
# V1.0: Gustavo Panizzo 2018-11-18
# V1.1: Ricardo Fraile 2018-11-21
__version__ = '1.1'

# Default Tuptime db location
TUPT_DBF = '/var/lib/tuptime/tuptime.db'

# Temporary file for Tuptime db
TUPT_TMP_DBF = '/tmp/tuptime-%s.db' % os.getpid()

# Backup for the current Tuptime db, if exists
TUPT_BACKUP = '/var/tmp/tuptime-%s.db.backup' % os.getpid()

# Overwrite toggle
REPLACE_DBF = False

# Location of uptimed records file (format uptime:btime:kernel)
UPTIME_RECORDS_FILE = '/var/spool/uptimed/records'



def insert_row(row):
    """ inserts a uptimed record as a row """

    conn = sqlite3.connect(TUPT_TMP_DBF)
    uptime = row[0]
    btime = row[1]
    kernel = row[2]
    _offbtime = row[3]
    downtime = row[4]
    endst = row[5]
    params = [btime, uptime, _offbtime, endst, downtime, kernel]
    print(str(params))

    conn.execute("INSERT INTO tuptime VALUES (?,?,?,?,?,?)", params)
    conn.commit()
    conn.close()



def create_db(db_file):
    """ creates a sqlite file and the tables required for tuptime. """

    print('+ Creating Tuptime temp db file: ' + str(db_file) + '\n')

    if os.path.isfile(db_file):
        logging.error('DB exists: ' + (db_file))
        raise SystemExit

    db_conn = sqlite3.connect(db_file)
    conn = db_conn.cursor()
    conn.execute('create table if not exists tuptime'
                 '(btime integer,'
                 'uptime real,'
                 'offbtime integer,'
                 'endst integer,'
                 'downtime real,'
                 'kernel text)')
    db_conn.commit()
    db_conn.close()



def read_uptime_records(file):
    """ returns uptimed records in a list """

    print('+ Reading Uptimed file: ' + UPTIME_RECORDS_FILE + '\n')

    # Read file and split records
    uptimed_records = []
    try:
        with open(file) as records:
            for line in records:
                line = line.rstrip()
                line = line.split(':')
                uptimed_records.append(line)
    except Exception as exc:
        sys.exit(exc)

    # Order by btime and reverse by uptime
    uptimed_records = sorted(uptimed_records, key=lambda x: (int(x[1]), -int(x[0])))

    # Exclude invalid records
    uptimed_clean_records = []
    offbtime = None
    for i, line in enumerate(uptimed_records):
        if i > 0:

            # If btime is lower than previous btime + uptime
            if int(line[1]) < int(offbtime):
                print('Exclude btime overlap --> ' + str(line))
                continue

            # If is negative
            if int(line[0]) < 0:  # uptime < 0
                print('Exclude uptime negative --> ' + str(line))
                continue

        offbtime = int(line[0]) + int(line[1])  # uptime + btime
        print(line)
        uptimed_clean_records.append(line)

    print('Total valid records: ' + str(len(uptimed_clean_records)) + '\n')

    if not len(uptimed_clean_records):
        logging.error('Any records to migrate from uptimed')
        raise SystemExit

    return uptimed_clean_records



def uptimed_to_tuptime(uptimed):
    """ converts records from uptimed format to tuptime's format """

    # Create tuptime content:
    #     uptime, btime, kernel + offbtime, downtime, endst
    newrecords = []
    for i, line in enumerate(uptimed):

        # Current offbtime
        offbtime = int(line[0]) + int(line[1])
        line.append(offbtime)

        if i > 0:
            # Previous downtime
            prev_downtime = int(line[1]) - int(newrecords[i-1][3])  # btime - prev.offbtime
            newrecords[i-1].append(prev_downtime)
            # Previous shutdown status
            newrecords[i-1].append('1')
        newrecords.append(line)

    # Reset last line
    newrecords[-1][3] = '-1'  # offbtime
    newrecords[-1].append('0.0')  # downtime
    newrecords[-1].append('1')  # endst

    if not len(newrecords):
        logging.error('Any records to migrate to Tuptime')
        raise SystemExit

    return newrecords



def substitution():
    """ test db result and copy to default location """

    print('\n+ Checking Tuptime execution over temp db file \n')

    if os.system("tuptime -tf " + TUPT_TMP_DBF) != 0:
        logging.error('Tuptime temp execution fails.')
        raise SystemExit

    if REPLACE_DBF:
        print('\n+ Moving temp db file to default Tuptime location: ' + TUPT_DBF)
        try:
            copyfile(TUPT_TMP_DBF, TUPT_DBF)
        except Exception as excp:
            sys.exit(excp)

        print('\n+ Setting user and group\n')
        user = os.stat(os.path.dirname(TUPT_DBF)).st_uid
        group = os.stat(os.path.dirname(TUPT_DBF)).st_gid
        os.chown(TUPT_DBF, user, group)
    else:
        print("\n(run with \'--replace\' to apply changes)")

    print('+ Done \n')



def checks():
    """ validate requirements """

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--replace',
        dest='replace',
        action='store_true',
        default=False,
        help='Replace default Tuptime db file'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='version ' + (__version__),
        help='show version'
    )
    arg = parser.parse_args()
    if arg.replace:
        global REPLACE_DBF
        REPLACE_DBF = True

    # Privileged user
    if os.geteuid() != 0:
        logging.error('Execute with a privileged user')
        raise SystemExit

    # Tuptime present
    if not which('tuptime'):
        logging.error('Tuptime not installed')
        raise SystemExit

    # Uptime file exists
    if not os.access(UPTIME_RECORDS_FILE, os.R_OK):
        logging.error('Can\'t read ' + UPTIME_RECORDS_FILE)
        raise SystemExit

    # Backup default Tuptime db file if exists
    if os.path.isfile(TUPT_DBF):
        try:
            copyfile(TUPT_DBF, TUPT_BACKUP)
        except Exception as excp:
            sys.exit(excp)
        print('Backup current Tuptime db file to ' + TUPT_BACKUP + '\n')



def main():
    """ Main migration steps """

    print('\n####  Uptimed to Tuptime migration script  ####\n')

    checks()
    uptimed_records = read_uptime_records(UPTIME_RECORDS_FILE)
    newrecords = uptimed_to_tuptime(uptimed_records)
    create_db(TUPT_TMP_DBF)
    for record in newrecords:
        insert_row(record)
    substitution()


if __name__ == "__main__":
    main()
