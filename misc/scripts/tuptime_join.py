#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script join two tuptime db files into an other one. It works as follows:

    - Takes two paths of db files and an output file as destination of the join.
    - Look for first btime on both files and take the one with the older value as starting DB
    - Look on starting DB for last register and sum (btime + uptime)
    - Look on the newer file for a btime greater than previous sum value
    - Insert registers that match on destination file DB

 # tuptime_join.py /path/to/old.db /path/to/new.db -d /path/to/joined.db

Maybe after upgrade your computer and install new stuff, you want to continue with the registers
that you have before. It is possible to join the new ones into the old ones without any awkward jump.
Please, see the following example:

Join registers of two db files into other:
    tuptime_join.py /backup/old/tuptime.db /var/lib/tuptime/tuptime.db -d /tmp/tt.db

Check if all is ok:
    tuptime --noup -t -f /tmp/tt.db

Check owner (usually tuptime:tuptime) and copy modified file to right location. Re-check owner:
    ls -al /var/lib/tuptime/tuptime.db
    cp /tmp/tt.db /var/lib/tuptime/tuptime.db
    ls -al /var/lib/tuptime/tuptime.db

'''

import sys, argparse, locale, signal, logging, sqlite3
from shutil import copyfile

__version__ = '1.2.0'

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
        help='files to join'
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
        action='count',
        default=0,
        help='verbose output (vv=detail)'
    )
    arg = parser.parse_args()

    if arg.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info('Version: %s', (__version__))

    logging.info('Arguments: %s', str(vars(arg)))
    return arg


def order_files(arg):
    """Identify older file"""

    # Open file0 DB
    db_conn0 = sqlite3.connect(arg.files[0])
    db_conn0.row_factory = sqlite3.Row
    conn0 = db_conn0.cursor()

    # Open file1 DB
    db_conn1 = sqlite3.connect(arg.files[1])
    db_conn1.row_factory = sqlite3.Row
    conn1 = db_conn1.cursor()

    # Check if DBs have the old format
    for conn, fname in ((conn0, arg.files[0]), (conn1, arg.files[1])):
        columns = [i[1] for i in conn.execute('PRAGMA table_info(tuptime)')]
        if 'rntime' and 'slptime' and 'bootid' not in columns:
            logging.error('DB format outdated on file: ' + str(fname))
            sys.exit(-1)

    # Check older file
    conn0.execute('select btime from tuptime where rowid = (select min(rowid) from tuptime)')
    conn1.execute('select btime from tuptime where rowid = (select min(rowid) from tuptime)')

    # File with large btime is newer
    if (conn0.fetchone()[0]) > (conn1.fetchone()[0]):
        return arg.files[1], arg.files[0]
    return arg.files[0], arg.files[1]


def main():
    """Main logic"""

    arg = get_arguments()

    f_old, f_new = order_files(arg)

    print('Old source file: \t' + str(f_old))
    print('New source file:\t' + str(f_new))

    # Use old file as starting DB. Copy as destination file.
    copyfile(f_old, arg.dest)
    fl0 = {'path': arg.dest}   # file0 is destination file
    fl1 = {'path': f_new}  # file1 is source newer file
    print('Destination file: \t' + str(fl0['path']))

    # Open file0 DB
    db_conn0 = sqlite3.connect(fl0['path'])
    db_conn0.row_factory = sqlite3.Row
    conn0 = db_conn0.cursor()

    # Open file1 DB
    db_conn1 = sqlite3.connect(fl1['path'])
    db_conn1.row_factory = sqlite3.Row
    conn1 = db_conn1.cursor()

    # Get all rows from source file0 and print raw rows
    conn0.execute('select rowid as startup, * from tuptime')
    db_rows = conn0.fetchall()
    print('\nDestination rows before:\t' + str(len(db_rows)))
    if arg.verbose > 1:
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    # Get last startup, btime and uptime from last row on file0 to calculate offbtime
    conn0.execute('select rowid, btime, uptime from tuptime where rowid = (select max(rowid) from tuptime)')
    fl0['startup'], fl0['btime'], fl0['uptime'] = conn0.fetchone()
    fl0['offbtime'] = fl0['btime'] + fl0['uptime']

    # Get all rows from file1 where btime is greater than file0 offbtime
    conn1.execute('select rowid as startup, * from tuptime where btime > ' + str(fl0['offbtime']))
    db_rows = conn1.fetchall()

    print('\nRows to add from newer file: \t' + str(len(db_rows)))

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
    if arg.verbose > 1:
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    db_conn0.close()
    db_conn1.close()
    print('\nDone.')


if __name__ == "__main__":
    main()
