#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess, csv, argparse, tempfile
from datetime import datetime, timedelta
from matplotlib.lines import Line2D
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

    ftmp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv

    # Get datetime objects from date limits in timestamp format
    tsince = str(int(dateutil.parser.parse(date_limits[0]).timestamp()))
    tuntil = str(int(dateutil.parser.parse(date_limits[1]).timestamp()))

    with open(ftmp, "wb", 0) as out:
        if arg.dbfile:  # If a file is passed, avoid update it
            subprocess.call(["tuptime", "-tsc", "--tsince", tsince, "--tuntil", tuntil, "-f", arg.dbfile, "-n"], stdout=out)
        else:
            subprocess.call(["tuptime", "-tsc", "--tsince", tsince, "--tuntil", tuntil], stdout=out)

    tstamp = []  # startup and shutdown timestamps
    color = []  # colors

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
            #print('-')

            if row[1] != '' and row[3] != '':
                tstamp.append(row[1])
                color.append('forestgreen')

                tstamp.append(row[3])
                if row[4] == 'BAD':
                    color.append('black')
                else:
                    color.append('grey')

    # Convert to datetime object
    tstamp = [datetime.fromtimestamp(int(elem)) for elem in tstamp]

    # Reset date allows position circles inside the same 00..24 range on y-axis
    y = [elem.replace(year=1970, month=1, day=1) for elem in tstamp]

    # Reset hour allows position circles straight over the date tick on x-axis
    x = [elem.replace(hour=00, minute=00, second=00) for elem in tstamp]

    # Set scatter plot values
    plt.scatter(x, y, s=200, color=color, edgecolors='white', alpha=0.8, marker="X")

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

    # Set legend
    plt.legend(handles=[Line2D([0], [0], marker='X', color='w', alpha=0.8, label='Startup', markerfacecolor='forestgreen', markersize=10),
                        Line2D([0], [0], marker='X', color='w', alpha=0.8, label='Shutdown Ok', markerfacecolor='grey', markersize=10),
                        Line2D([0], [0], marker='X', color='w', alpha=0.8, label='Shutdown Bad', markerfacecolor='black', markersize=10)])

    axs.set_axisbelow(True)
    axs.invert_yaxis()
    axs.grid(True)

    plt.ylabel('Day Time')
    plt.title('Events on Time by Day')
    plt.margins(y=0, x=0.01)
    plt.grid(color='lightgrey', linestyle='--', linewidth=0.9, axis='y')
    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.show()

if __name__ == "__main__":
    main()
