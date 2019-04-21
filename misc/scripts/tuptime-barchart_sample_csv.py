#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sample plot report from the info that the tuptime command report"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import dateutil.parser
import subprocess, csv, argparse, tempfile


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
        help='end date to plot, format:"Y-m-d". Default edate is today.',
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
        '-p', '--pastdays',
        dest='pdays',
        default=7,
        action='store',
        help='past days before edate to plot, will be ignored if set bdate (default is 7).',
        type=int
    )
    arg = parser.parse_args()
    return arg


def date_check(arg):
    """Check and clean dates"""

    # Set user or default begind date. Days ago...
    if arg.bdate:
        begin_date = dateutil.parser.parse(arg.bdate)
    else:
        begin_date = datetime.today() - timedelta(days=arg.pdays)
        print('Default begin:\t' + str(arg.pdays) + ' days ago')

    # Set user or default end date.
    if arg.edate:
        end_date = dateutil.parser.parse(arg.edate)
    else:
        end_date = datetime.today()
        print('Default end:\tnow')

    # Adjust date to the start or end time range and set the format
    begin_date = begin_date.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    end_date = end_date.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")

    print('Begin date:\t' + str(begin_date))
    print('End date:\t' + str(end_date))

    return([begin_date, end_date])


def date_range(date_limits):
    """Get the range of dates to apply"""

    dlimit = []  # Store date range in human date
    ranepo = []  # Store date range in epoch
    xlegend = []  # legend to x axis

    dstart = dateutil.parser.parse(date_limits[0])  # Start date
    dend = dateutil.parser.parse(date_limits[1])  # End date

    # Split time range in days and finally add the rest (minnor than one day)
    while dstart <= dend:
        dlimit.append(dstart)
        dstart += timedelta(days=1)
    dlimit.append(dend)

    print('Date splits:\t' + str(len(dlimit)))

    # Create list with lists of two epoch dates, begin and end for each split
    reg = 1
    while reg < len(dlimit):
        ranepo.append([dlimit[reg-1].timestamp(), dlimit[reg].timestamp()])
        xlegend.append(datetime.fromtimestamp(dlimit[reg-1].timestamp()).strftime('%Y-%m-%d'))
        reg += 1

    print('Ranges on list:\t' + str(len(ranepo)))

    return(ranepo, xlegend)


def main():
    """Core logic"""

    arg = get_arguments()
    date_limits = date_check(arg)
    date_list, xlegend = date_range(date_limits)

    # Query to Tuptime with each range
    nran = 0  # Range number
    daysplt = []  # List for all day splits with their events.
    max_events = 0  # Max events in a daysplit
    ftemp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv

    # Iterate over each element in (since, until) list
    while nran < len(date_list):
        ar1 = str(int(date_list[nran][0]))  # Timestamp arg tsince
        ar2 = str(int(date_list[nran][1]))  # timestamp arg tuntil
        nran += 1  # Number of range

        # Save Tuptime csv output to file
        with open(ftemp, "wb", 0) as out:
            if arg.dbfile:  # If a file is passed, avoid update it
                subprocess.call(["tuptime", "-lsc", "--tsince", ar1, "--tuntil", ar2, "-f", arg.dbfile, "-n"], stdout=out)
            else:
                subprocess.call(["tuptime", "-lsc", "--tsince", ar1, "--tuntil", ar2], stdout=out)

        # Get csv file
        l_events = []  # List for events in each daysplt
        with open(ftemp) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            bad = None  # Register bad shutdown

            for row in csv_reader:
                l_row = []  # List for events in csv rows

                # Control how was the shutdown
                if (row[0] == 'Shutdown') and (row[1] == 'BAD'):
                    bad = True

                # This create a list with (uptime, downtime ok, downtime bad)
                if (row[0] == 'Uptime') or (row[0] == 'Downtime'):

                    if row[0] == 'Uptime':
                        # Add 0 or value to first position
                        l_row.append(int(round(float(row[1]), 0)))
                    else:
                        l_row.append(0)

                    if row[0] == 'Downtime':
                        # Add (0, value) or (value, 0) to the end
                        if bad is True:
                            l_row.extend((0, int(round(float(row[1]), 0))))
                        else:
                            l_row.extend((int(round(float(row[1]), 0)), 0))
                        bad = False  # Reset false
                    else:
                        l_row.extend((0, 0))

                    # Add to events list
                    l_events.append(l_row)

            # Add to daysplt list
            daysplt.append(l_events)

            print('Got range --->\t' + str(nran) + ' with ' + str(len(l_events)) + ' events')

            # Catch large l_events list
            if len(l_events) > max_events:
                max_events = len(l_events)

    print('Ranges got:\t' + str(len(daysplt)))

    # Convert seconds to days to plot them
    for i in range(0, len(daysplt)):
        for k in range(0, len(daysplt[i])):
            daysplt[i][k][:] = [x / 3600 for x in daysplt[i][k]]

    # All days with equal number of events, fill with 0,0,0
    for i in range(0, len(daysplt)):
        while max_events > len(daysplt[i]):
            daysplt[i].append([0, 0, 0])

    # Stack events from each day (daysplt) based on their position
    #  upt, downt ok, downt bad, upt, downt ok, and so on...
    stack = []
    for k in range(0, max_events):
        for n in range(0, 3):
            position1 = []
            for u in range(0, len(daysplt)):
                position1.append(daysplt[u][k][n])
            stack.append(np.array(position1))

    print('Rows to stack:\t' + str(len(stack)))

    ind = np.arange(len(daysplt))    # the x locations for the groups
    width = 0.9
    color_list = ['green', 'grey', 'black']

    # Plot events from their position and rotate color
    for i in range(0, len(stack)):
        plt.bar(ind, stack[i], width, color=color_list[i % len(color_list)], linewidth=0, bottom=np.sum(stack[:i], axis=0))

    plt.ylabel('Hours')
    plt.title('Tuptime bar chart')
    plt.xticks(ind, xlegend, rotation=15)
    plt.margins(y=0, x=0.01)
    plt.yticks(np.arange(0, 25, 2))
    plt.grid(color='w', linestyle='--', linewidth=0.5, axis='y')
    plt.show()

if __name__ == "__main__":
    main()
