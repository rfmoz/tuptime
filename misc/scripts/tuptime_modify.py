#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script modify the 'Startup Date' and 'Shutdown Date' on Tuptime database
keeping the other values around in sync.

Increase 60 secs the startup date on register number 1:
    tuptime_modify.py -c startup -r 1 -s 60

Decrease 100 secs the startup date on register number 4 on other file:
    tuptime_modify.py -c startup -r 4 -s -100 -f /tmp/test.db

Increase 30 secs the shutdown date on register number 12:
    tuptime_modify.py -c shutdown -r 12 -s 60

Decrease 300 secs the shutdown date on register number 47 with verbose:
    tuptime_modify.py -c shutdown -r 47 -s -300 -v

'''

import sys, argparse, locale, signal, logging, sqlite3, tempfile
from shutil import copyfile

DB_FILE = '/var/lib/tuptime/tuptime.db'
DATE_FORMAT = '%X %x'
__version__ = '1.0.0'

# Terminate when SIGPIPE signal is received
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Set locale to the users default settings (LANG env. var)
locale.setlocale(locale.LC_ALL, '')


def get_arguments():
    """Get arguments from command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--change',
        dest='change',
        default=False,
        action='store',
        type=str,
        required=True,
        choices=['startup', 'shutdown'],
        help='change startup or shutdown date time [<startup|shutdown>]'
    )
    parser.add_argument(
        '-f', '--filedb',
        dest='db_file',
        default=DB_FILE,
        action='store',
        help='database file (' + DB_FILE + ')',
        metavar='FILE'
    )
    parser.add_argument(
        '-n', '--nobackup',
        dest='nobackup',
        default=False,
        action='store_true',
        help='avoid create backup db file'
    )
    parser.add_argument(
        '-r', '--register',
        dest='register',
        default=False,
        action='store',
        type=int,
        required=True,
        help='startup register to modify'
    )
    parser.add_argument(
        '-s', '--seconds',
        dest='seconds',
        default=0,
        action='store',
        type=int,
        required=True,
        help='seconds to add or remove (+/-)'
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


def backup_dbf(arg):
    """Backup db file before modify"""

    try:
        tmp_file = tempfile.NamedTemporaryFile(prefix="tuptime_", suffix=".db").name

        copyfile(arg.db_file, tmp_file)
        print('Backup file:\t' + tmp_file)
    except Exception as exp:
        logging.error('Can\'t create backup file. %s', str(exp))
        sys.exit(-1)


def fix_shutdown(arg, reg, conn, modt, orgt):
    """Modify shutdown date register"""

    # Last row have None values
    if orgt['offbtime'] is not None and orgt['downtime'] is not None:
        modt['offbtime'] = orgt['offbtime'] + arg.seconds
        modt['downtime'] = orgt['downtime'] - arg.seconds
    else:
        modt['offbtime'] = None
        modt['downtime'] = None
    modt['uptime'] = orgt['uptime'] + arg.seconds
    modt['rntime'] = orgt['rntime'] + arg.seconds

    print('\t   modified\tbtime:    n/a     | uptime: ' + str(modt['uptime']) + ' | rntime: ' + str(modt['rntime']) + ' | offbtime: ' + str(modt['offbtime']) + ' | downtime: ' + str(modt['downtime']))

    # Limit check
    if modt['downtime'] is None or modt['downtime'] <= 0 or \
       modt['offbtime'] is None or modt['offbtime'] <= 0 or \
       modt['uptime'] <= 0 or modt['rntime'] <= 0:
        logging.error('modified values can\'t be None or lower than 1')
        sys.exit(-1)

    # Update values
    conn.execute('update tuptime set uptime = ' + str(modt['uptime']) + ' where rowid = ' + str(reg['target']))
    conn.execute('update tuptime set rntime = ' + str(modt['rntime']) + ' where rowid = ' + str(reg['target']))
    conn.execute('update tuptime set downtime = ' + str(modt['downtime']) + ' where rowid = ' + str(reg['target']))
    conn.execute('update tuptime set offbtime = ' + str(modt['offbtime']) + ' where rowid = ' + str(reg['target']))


def fix_startup(arg, reg, conn, modt, orgt, modp, orgp):
    """Modify startup date register"""

    modt['btime'] = orgt['btime'] + arg.seconds
    modt['uptime'] = orgt['uptime'] - arg.seconds
    modt['rntime'] = orgt['rntime'] - arg.seconds

    print('\t   modified\tbtime: ' + str(modt['btime']) + ' | uptime: ' + str(modt['uptime']) + ' | rntime: ' + str(modt['rntime']) + ' | offbtime: ----n/a--- | downtime: --n/a-- ')

    # Limit check
    if modt['uptime'] <= 0 or modt['rntime'] <= 0:
        logging.error('modified values can\'t be lower than 1')
        sys.exit(-1)

    # First row don't have previous register to modify
    if reg['prev'] > 0:

        # Get values from previous register
        conn.execute('select downtime from tuptime where rowid = ' + str(reg['prev']))
        orgp['downtime'] = conn.fetchone()[0]

        modp['downtime'] = orgp['downtime'] + arg.seconds

        print('\tTarget row-1 (startup: ' + str(reg['prev']) + ')')
        print('\t   original\tdowntime: ' + str(orgp['downtime']))
        print('\t   modified\tdowntime: ' + str(modp['downtime']))

        # Limit check
        if modp['downtime'] <= 0:
            logging.error('downtime can\'t be lower than 1')
            sys.exit(-1)

        conn.execute('update tuptime set downtime = ' + str(modp['downtime']) + ' where rowid = ' + str(reg['prev']))

    # Update values
    conn.execute('update tuptime set btime = ' + str(modt['btime']) + ' where rowid = ' + str(reg['target']))
    conn.execute('update tuptime set uptime = ' + str(modt['uptime']) + ' where rowid = ' + str(reg['target']))
    conn.execute('update tuptime set rntime = ' + str(modt['rntime']) + ' where rowid = ' + str(reg['target']))


def main():

    arg = get_arguments()
    orgt = {}  # Original target value
    orgp = {}  # Original previous (target-1) value
    modt = {}  # Modified target value
    modp = {}  # Modified previous (target-1) value
    reg = {'target': arg.register, 'prev': (arg.register - 1)}  # Target register to modify and previous one

    print('Target file:\t' + arg.db_file)
    if not arg.nobackup:
        backup_dbf(arg)

    db_conn = sqlite3.connect(arg.db_file)
    db_conn.row_factory = sqlite3.Row
    conn = db_conn.cursor()

    # Check if DB have the old format
    columns = [i[1] for i in conn.execute('PRAGMA table_info(tuptime)')]
    if 'rntime' and 'slptime' not in columns:
        logging.error('DB format outdated')
        sys.exit(-1)

    # Print raw rows
    if arg.verbose:
        print('\nTarget registers before: ')
        conn.execute('select rowid as startup, * from tuptime where rowid between ' + str(reg['prev']) + ' and ' + str(reg['target']))
        db_rows = conn.fetchall()
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    # Validate register to modify
    conn.execute('select max(rowid) from tuptime')
    max_register = conn.fetchone()[0]
    if reg['target'] > max_register or reg['target'] < 1:
        logging.error('Invalid register to modify. Out of range')
        sys.exit(-1)

    # Get values from target row
    conn.execute('select btime, uptime, rntime, offbtime, downtime from tuptime where rowid = ' + str(reg['target']))
    orgt['btime'], orgt['uptime'], orgt['rntime'], orgt['offbtime'], orgt['downtime'] = conn.fetchone()

    print('\nValues:')
    print('\tTarget row   (startup: ' + str(reg['target']) + ')')
    print('\t   original\tbtime: ' + str(orgt['btime']) + ' | uptime: ' + str(orgt['uptime']) + ' | rntime: ' + str(orgt['rntime']) + ' | offbtime: ' + str(orgt['offbtime']) + ' | downtime: ' + str(orgt['downtime']))

    # Modify startup or shutdown date
    if arg.change == 'startup':
        fix_startup(arg, reg, conn, modt, orgt, modp, orgp)
    if arg.change == 'shutdown':
        fix_shutdown(arg, reg, conn, modt, orgt)

    db_conn.commit()

    # Print raw rows
    if arg.verbose:
        print('\nTarget registers after: ')
        conn.execute('select rowid as startup, * from tuptime where rowid between ' + str(reg['prev']) + ' and ' + str(reg['target']))
        db_rows = conn.fetchall()
        for row in db_rows:
            print("\t", end='')
            print(dict(row))

    db_conn.close()
    print('\nDone.')


if __name__ == "__main__":
    main()
