#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script join two tuptime db files into an other one. It works as follows:

    - Takes two paths of db files (old one must be first) and an output file as destination of the join.
    - Look for last register on old file and sum (btime + uptime)
    - Look on new file a btime greather than previous sum value
    - Insert registers that match

 # tuptime_join.py -d /path/to/joined.db /path/to/old.db /path/to/new.db

Maybe after upgrade your computer and install new stuff, you want to continue with the registers
that you have before. It is possible to join the new ones into the old ones without any awkward jump.
Please, see the following example:

Join new registers of two db files into other (old file must be defined first):
    tuptime_join.py -d /tmp/tt.db /backup/old/tuptime.db /var/lib/tuptime/tuptime.db

Check if all is ok:
    tuptime --noup -t -f /tmp/tt.db

Check owner (usually tuptime:tuptime) and copy modified file to right location. Re-check owner:
    ls -al /var/lib/tuptime/tuptime.db
    cp /tmp/tt.db /var/lib/tuptime/tuptime.db
    ls -al /var/lib/tuptime/tuptime.db

'''

import sys, argparse, locale, signal, logging, sqlite3
from shutil import copyfile

__version__ = '1.1.0'

# Terminate when SIGPIPE signal is received
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Set locale to the users default settings (LANG env. var)
locale.setlocale(locale.LC_ALL, '')


def get_arguments():
    """Get arguments from command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs=2,
        type=str,
        help='files to join (OLD and NEW)'
    )
    parser.add_argument(
        '-d', '--dest',
        dest='dest',
        default=False,
        action='store',
        type=str,
        required=True,
        help='destination file to store join'
    )
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help='verbose output'
    )
    arg = parser.parse_args()

    if arg.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info('Version: %s', (__version__))

    logging.info('Arguments: %s', str(vars(arg)))
    return arg


def main():

    arg = get_arguments()

    print('Old file (arg 1): \t' + str(arg.files[0]))
    print('New file (arg 2):\t' + str(arg.files[1]))

    # Copy old file to output file
    print('\nCopy old file to destination')
    copyfile(arg.files[0], arg.dest)
    fl0 = {'name': arg.dest}    # File0 is output file
    fl1 = {'name': arg.files[1]}  # file1 is new file
    print('Destination file: \t' + str(fl0['name']))

    # Open file0 DB
    db_conn0 = sqlite3.connect(fl0['name'])
    db_conn0.row_factory = sqlite3.Row
    conn0 = db_conn0.cursor()

    # Check if DB have the old format
    columns = [i[1] for i in conn0.execute('PRAGMA table_info(tuptime)')]
    if 'rntime' and 'slptime' and 'bootid' not in columns:
        logging.error('DB format outdated on old file')
        sys.exit(-1)

    # Open file1 DB
    db_conn1 = sqlite3.connect(fl1['name'])
    db_conn1.row_factory = sqlite3.Row
    conn1 = db_conn1.cursor()

    # Check if DB have the old format
    columns = [i[1] for i in conn1.execute('PRAGMA table_info(tuptime)')]
    if 'rntime' and 'slptime' and 'bootid' not in columns:
        logging.error('DB format outdated on new file')
        sys.exit(-1)

    # Check older file
    conn0.execute('select btime from tuptime where rowid = (select min(rowid) from tuptime)')
    fl0_btime = conn0.fetchone()[0]
    conn1.execute('select btime from tuptime where rowid = (select min(rowid) from tuptime)')
    fl1_btime = conn1.fetchone()[0]
    if fl0_btime > fl1_btime:
        logging.warning('"New file" looks older than "Old file"')

    # Print raw rows
    conn0.execute('select rowid as startup, * from tuptime')
    db_rows = conn0.fetchall()
    print('\nDestination rows before:\t' + str(len(db_rows)))
    if arg.verbose:
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    # Get last startup, btime and uptime from last row on file0 to calculate offbtime
    conn0.execute('select rowid, btime, uptime from tuptime where rowid = (select max(rowid) from tuptime)')
    fl0['startup'], fl0['btime'], fl0['uptime'] = conn0.fetchone()
    fl0['offbtime'] = fl0['btime'] + fl0['uptime']

    # Get all rows from file1 where btime is greather than file0 offbtime
    conn1.execute('select rowid as startup, * from tuptime where btime > ' + str(fl0['offbtime']))
    db_rows = conn1.fetchall()

    print('\nRows to add from new file: \t' + str(len(db_rows)))

    # Insert rows on file0
    for row in db_rows:

        # At first row on file1, set offbtime, endst and downtime to last row on file0
        if row == db_rows[0]:

            print(' Fix shutdown values on row: ' + str(fl0['startup']))
            fl0['downtime'] = row['btime'] - fl0['offbtime']
            conn0.execute('update tuptime set offbtime = ' + str(fl0['offbtime']) + ', endst = 1, downtime = ' + str(fl0['downtime']) +
                          ' where rowid = (select max(rowid) from tuptime)')
            if arg.verbose:
                print('\toffbtime = ' + str(fl0['offbtime']))
                print('\tendst = 1')
                print('\tdowntime = ' + str(fl0['downtime']))

        # Add registers to file0
        print(' Adding startup row: ' + str(row['startup']))
        conn0.execute('insert into tuptime values (?,?,?,?,?,?,?,?,?)',
                      (str(row['bootid']), str(row['btime']), str(row['uptime']), str(row['rntime']), str(row['slptime']), str(row['offbtime']), str(row['endst']), str(row['downtime']), str(row['kernel'])))
        if arg.verbose:
            print('\tbootid = ' + str(row['bootid']))
            print('\tbtime = ' + str(row['btime']))
            print('\tuptime = ' + str(row['uptime']))
            print('\trntime = ' + str(row['rntime']))
            print('\tslptime = ' + str(row['slptime']))
            print('\toffbtime = ' + str(row['offbtime']))
            print('\tendst = ' + str(row['endst']))
            print('\tdowntime = ' + str(row['downtime']))
            print('\tkernel = ' + str(row['kernel']))

        # At last row, empty offbtime, endst and downtime
        if row == db_rows[-1]:
            print(' Fix shutdown values on last row')
            conn0.execute('update tuptime set offbtime = NULL, endst = 0, downtime = NULL where rowid = (select max(rowid) from tuptime)')

    db_conn0.commit()

    # Print raw rows
    conn0.execute('select rowid as startup, * from tuptime')
    db_rows = conn0.fetchall()
    print('\nDestination rows after: \t' + str(len(db_rows)))
    if arg.verbose:
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    db_conn0.close()
    db_conn1.close()
    print('\nDone.')


if __name__ == "__main__":
    main()
