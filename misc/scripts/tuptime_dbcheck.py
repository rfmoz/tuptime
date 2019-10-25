#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test database integrity. Try to catch weird errors and fix them.
'''

import sys, argparse, locale, signal, logging, sqlite3

__version__ = '1.0.0'
DB_FILE = '/var/lib/tuptime/tuptime.db'
fixcnt = 0

# List of tests to auto-execute
TESTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Terminate when SIGPIPE signal is received
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Set locale to the users default settings (LANG env. var)
locale.setlocale(locale.LC_ALL, '')


def get_arguments():
    """Get arguments from command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--filedb',
        dest='db_file',
        default=DB_FILE,
        action='store',
        help='database file (' + DB_FILE + ')',
        metavar='FILE'
    )
    parser.add_argument(
        '--fix',
        dest='fix',
        default=False,
        action='store_true',
        help='try to fix errors automatically'
    )
    parser.add_argument(
        '-t', '--test',
        dest='test',
        nargs='+',
        type=int,
        default=TESTS,
        help='list of test to execute'
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


def fix_cnt():
    global fixcnt
    fixcnt += 1


def test0(arg, db_rows, conn):
    if len(db_rows) != db_rows[-1]['startup']:
        print(' Possible deleted rows in db. Real startups are not equal to enumerate startups')

        if arg.fix:
            conn.execute('vacuum')
            print(' FIXED: vacuum')
            fix_cnt()


def test1(arg, row, conn):
    if row['offbtime'] and \
       row['btime'] > row['offbtime']:
        print(row['startup'])
        print(' row btime > offbtime')
        print(' ' + str(row['btime']) + ' > ' + str(row['offbtime']))

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()


def test2(arg, row, conn, prev_row):
    if prev_row['offbtime'] > row['btime']:
        print(row['startup'])
        print(' prev_row offbtime > btime')
        print(' ' + str(prev_row['offbtime']) + ' > ' + str(row['btime']))

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()


def test3(arg, row, conn, prev_row):
    if prev_row['offbtime'] + prev_row['downtime'] != row['btime']:
        print(row['startup'])
        print(' prev_row offbtime + prev_row downtime != btime')
        print(' ' + str(prev_row['offbtime']) + ' + ' + str(prev_row['downtime']) + ' != ' + str(row['btime']))

        if arg.fix:
            fixed = row['btime'] - prev_row['offbtime']
            conn.execute('update tuptime set downtime = ' + str(fixed) + ' where rowid = ' + str(row['startup'] - 1))
            print(' FIXED: prev_row downtime = ' + str(fixed))
            fix_cnt()


def test4(arg, row, conn):
    if row['offbtime'] and \
       row['btime'] + row['uptime'] != row['offbtime']:
        print(row['startup'])
        print(' row btime + uptime != offbtime')
        print(' ' + str(row['btime']) + ' + ' + str(row['uptime']) + ' != ' + str(row['offbtime']))

        if arg.fix:
            fixed = row['offbtime'] - row['btime']
            conn.execute('update tuptime set uptime = ' + str(fixed) + ' where rowid = ' + str(row['startup']))
            print(' FIXED: uptime = ' + str(fixed))
            fix_cnt()


def test5(arg, row, conn):
    if row['rntime'] + row['slptime'] != row['uptime']:
        print(row['startup'])
        print(' rntime + slptime != uptime')
        print(' ' + str(row['rntime']) + ' + ' + str(row['slptime']) + ' != ' + str(row['uptime']))

        if arg.fix:
            fixed = row['rntime'] + row['slptime'] - row['uptime']
            if row['rntime'] > row['slptime'] and row['rntime'] - fixed > 0:
                fixed2 = row['rntime'] - fixed
                conn.execute('update tuptime set rntime = ' + str(fixed2) + ' where rowid = ' + str(row['startup']))
                print(' FIXED: rntime = ' + str(fixed2))
            elif row['slptime'] > row['rntime'] and row['slptime'] - fixed > 0:
                fixed2 = row['slptime'] - fixed
                conn.execute('update tuptime set slptime = ' + str(fixed2) + ' where rowid = ' + str(row['startup']))
                print(' FIXED: slptime = ' + str(fixed2))
            else:
                conn.execute('update tuptime set rntime = ' + str(row['uptime']) + ', slptime = 0 where rowid = ' + str(row['startup']))
                print(' FIXED: rntime = ' + str(row['uptime']))
                print(' FIXED: slptime = 0')
            fix_cnt()


def test6(arg, row, conn):
    if row['uptime'] < 0:
        print(row['startup'])
        print(' uptime < 0')
        print(' ' + str(row['uptime']) + ' < 0')

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()


def test7(arg, row, conn):
    if row['rntime'] < 0:
        print(row['startup'])
        print(' rntime < 0')
        print(' ' + str(row['rntime']) + ' < 0')

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()


def test8(arg, row, conn):
    if row['slptime'] < 0:
        print(row['startup'])
        print(' slptime < 0')
        print(' ' + str(row['slptime']) + ' < 0')

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()


def test9(arg, row, conn):
    if row['downtime'] and \
       row['downtime'] < 0:
        print(row['startup'])
        print(' downtime < 0')
        print(' ' + str(row['downtime']) + ' < 0')

        if arg.fix:
            conn.execute('delete from tuptime where rowid = ' + str(row['startup']))
            print(' FIXED: delete row = ' + str(row['startup']))
            fix_cnt()



def main():

    arg = get_arguments()

    db_conn = sqlite3.connect(arg.db_file)
    db_conn.row_factory = sqlite3.Row
    conn = db_conn.cursor()

    # Check if DB have the old format
    columns = [i[1] for i in conn.execute('PRAGMA table_info(tuptime)')]
    if 'rntime' and 'slptime' not in columns:
        logging.error('DB format outdated')
        sys.exit(-1)

    print('Processing ' + str(arg.db_file) + ' --->')

    for i in arg.test:
        print('\n### ' + str(i) + ' ###')

        conn.execute('select rowid as startup, * from tuptime')
        db_rows = conn.fetchall()
        for row in db_rows:

            if arg.verbose:
                print('\n' + str(row['startup']) + '\n ' + str(dict(row)))

            if i == 1:
                test1(arg, row, conn)

            if i == 2:
                if row != db_rows[0]:  # Only after first row
                    test2(arg, row, conn, prev_row)

            if i == 3:
                if row != db_rows[0]:  # Only after first row
                    test3(arg, row, conn, prev_row)

            if i == 4:
                test4(arg, row, conn)

            if i == 5:
                test5(arg, row, conn)

            if i == 6:
                test6(arg, row, conn)

            if i == 7:
                test7(arg, row, conn)

            if i == 8:
                test8(arg, row, conn)

            if i == 9:
                test9(arg, row, conn)

            if i == 9:
                test9(arg, row, conn)

            prev_row = row

        if i == 10:
            test0(arg, db_rows, conn)

        db_conn.commit()

    db_conn.close()

    print('\n' + '-' * 25)
    print('Fixed: ' + str(fixcnt))
    print('Done.')


if __name__ == "__main__":
    main()
