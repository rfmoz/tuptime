#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess, csv, argparse, tempfile
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import dateutil.parser


def get_arguments():
    """Get arguments from command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b', '--bdate',
        dest='bdate',
        action='store',
        help='begin date to plot, format:"Y-m-d"',
        type=str
    )
    parser.add_argument(
        '-e', '--edate',
        dest='edate',
        action='store',
        help='end date to plot, format:"Y-m-d" (default today)',
        type=str
    )
    parser.add_argument(
        '-f', '--filedb',
        dest='dbfile',
        default=None,
        action='store',
        help='database file'
    )
    parser.add_argument(
        '-H', '--height',
        dest='height',
        default=13,
        action='store',
        help='window height in cm',
        type=int
    )
    parser.add_argument(
        '-p', '--pastdays',
        dest='pdays',
        default=7,
        action='store',
        help='past days before edate to plot (default is 7)',
        type=int
    )
    parser.add_argument(
        '-W', '--width',
        dest='width',
        default=17,
        action='store',
        help='window width in cm',
        type=int
    )
    parser.add_argument(
        '-x',
        dest='report_pie',
        action='store_true',
        default=False,
        help='swich to  pie report with accumulated hours'
    )
    arg = parser.parse_args()
    return arg


def date_check(arg):
    """Check and clean dates"""

    # Set user provided or default end date
    if arg.edate:
        end_date = dateutil.parser.parse(arg.edate)
    else:
        end_date = datetime.today()
        print('Default end:\tnow')

    # Set user provided or default begind date. Days ago...
    if arg.bdate:
        begin_date = dateutil.parser.parse(arg.bdate)
    else:
        begin_date = end_date - timedelta(days=arg.pdays)
        print('Default begin:\tsince ' + str(arg.pdays) + ' days ago')


    # Adjust date to the start or end time range and set the format
    begin_date = begin_date.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    end_date = end_date.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")

    print('Begin datetime:\t' + str(begin_date))
    print('End datetime:\t' + str(end_date))

    return([begin_date, end_date])



def main():
    """Core logic"""

    arg = get_arguments()
    date_limits = date_check(arg)

    ftmp = tempfile.NamedTemporaryFile().name  # For Tuptime csv file
    tst = {'up': [], 'down': [], 'down_ok': [], 'down_bad': []}  # Store events list on range

    # Get datetime objects from date limits in timestamp format
    tsince = str(int(dateutil.parser.parse(date_limits[0]).timestamp()))
    tuntil = str(int(dateutil.parser.parse(date_limits[1]).timestamp()))

    # Query tuptime for every (since, until) and save output to a file
    with open(ftmp, "wb", 0) as out:
        if arg.dbfile:  # If a file is passed, avoid update it
            subprocess.call(["tuptime", "-tsc", "--tsince", tsince, "--tuntil", tuntil, "-f", arg.dbfile, "-n"], stdout=out)
        else:
            subprocess.call(["tuptime", "-tsc", "--tsince", tsince, "--tuntil", tuntil], stdout=out)

    # Parse csv file
    with open(ftmp) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            if row[0] == 'No.':
                continue

            #print('Startup T.: ' + row[1])
            #print('Uptime: ' + row[2])
            #print('Shutdown T.: ' + row[3])
            #print('End: ' + row[4])
            #print('Downtime: ' + row[5])

            if row[1] != '':
                tst['up'].append(row[1])

            if row[3] != '':
                if row[4] == 'BAD':
                    tst['down_bad'].append(row[3])
                else:
                    tst['down_ok'].append(row[3])

    # Set whole downtimes and convert to datetime object
    tst['down'] = tst['down_ok'] + tst['down_bad']
    for state in tst:
        tst[state] = [datetime.fromtimestamp(int(elem)) for elem in tst[state]]

    if arg.report_pie:
        pie = {'up': [], 'down': []}  # One plot for each type

        # From datetime, get only hour and add 'h' at the end
        for elem in tst['up']: pie['up'].append(str(elem.hour) + str('h'))
        for elem in tst['down']: pie['down'].append(str(elem.hour) + str('h'))

        # Count elements on list or set None if emtpy
        c_down = dict(Counter(pie['down'])) if pie['down'] else {'None': [0]}
        c_up = dict(Counter(pie['up'])) if pie['up'] else {'None': [0]}

        # Set two plots and their frame size
        _, axs = plt.subplots(1, 2, figsize=((arg.width / 2.54), (arg.height / 2.54)))

        # Set values for each pie plot
        axs[0].pie([c_up[v] for v in c_up], labels=[k for k in c_up], autopct='%1.1f%%', textprops={'fontsize': 8})
        axs[0].set(aspect="equal", title='Startup')

        axs[1].pie([c_down[v] for v in c_down], labels=[k for k in c_down], autopct='%1.1f%%', textprops={'fontsize': 8})
        axs[1].set(aspect="equal", title='Shutdown')

        axs[0].text(1, -0.1, str('From    ' + str(date_limits[0]) + '    to    ' + str(date_limits[1])), size=10, ha="center", transform=axs[0].transAxes)
        plt.suptitle("Events per hour", fontsize=14)

    else:
        # Reset date allows position circles inside the same 00..24 range on y-axis
        scatt_y = {'up': [], 'down_ok': [], 'down_bad': []}
        scatt_y['up'] = [elem.replace(year=1970, month=1, day=1) for elem in tst['up']]
        scatt_y['down_ok'] = [elem.replace(year=1970, month=1, day=1) for elem in tst['down_ok']]
        scatt_y['down_bad'] = [elem.replace(year=1970, month=1, day=1) for elem in tst['down_bad']]

        # Reset hour allows position circles straight over the date tick on x-axis
        scatt_x = {'up': [], 'down_ok': [], 'down_bad': []}
        scatt_x['up'] = [elem.replace(hour=00, minute=00, second=00) for elem in tst['up']]
        scatt_x['down_ok'] = [elem.replace(hour=00, minute=00, second=00) for elem in tst['down_ok']]
        scatt_x['down_bad'] = [elem.replace(hour=00, minute=00, second=00) for elem in tst['down_bad']]

        # Set width and height from inches to cm
        plt.figure(figsize=((arg.width / 2.54), (arg.height / 2.54)))

        # Set scatter plot values
        plt.scatter(scatt_x['up'], scatt_y['up'], s=200, color='forestgreen', edgecolors='white', alpha=0.8, marker="X", label='Up')
        plt.scatter(scatt_x['down_ok'], scatt_y['down_ok'], s=200, color='grey', edgecolors='white', alpha=0.8, marker="X", label='Down ok')
        plt.scatter(scatt_x['down_bad'], scatt_y['down_bad'], s=200, color='black', edgecolors='white', alpha=0.8, marker="X", label='Down bad')

        # Format axes:
        plt.gcf().autofmt_xdate()
        axs = plt.gca()

        #  X as days and defined limits + 12h of margin
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%D'))
        axs.xaxis.set_major_locator(mdates.DayLocator())
        lbegin = datetime.strptime(date_limits[0], '%Y-%m-%d %H:%M:%S') - timedelta(hours=12)
        lend = datetime.strptime(date_limits[1], '%Y-%m-%d %H:%M:%S') + timedelta(hours=12)
        plt.xlim(lbegin, lend)

        #  Y as 24 hours range
        axs.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs.yaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 2)))
        plt.ylim([datetime(1970, 1, 1, 00, 00), datetime(1970, 1, 1, 23, 59, 59)])

        axs.set_axisbelow(True)
        axs.invert_yaxis()
        plt.grid(True)
        plt.ylabel('Day Time')
        plt.title('Events on Time by Day')
        plt.margins(y=0, x=0.01)
        plt.grid(color='lightgrey', linestyle='--', linewidth=0.9, axis='y')
        plt.legend()

    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.show()

if __name__ == "__main__":
    main()
