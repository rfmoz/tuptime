#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sample plot report from the info that the tuptime command report"""

#
# This is a playground script.
# It only test how to extract values from Tuptime and plot them in a
# graphic enviroment. It isn't 100% reliable, fails setting right
# position on first day and when DST happends.
#

from datetime import datetime, timedelta
import subprocess, csv, argparse, tempfile
import numpy as np
import matplotlib.pyplot as plt
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
        '-H', '--height',
        dest='height',
        default=6,
        action='store',
        help='window height.',
        type=int
    )
    parser.add_argument(
        '-p', '--pastdays',
        dest='pdays',
        default=7,
        action='store',
        help='past days before edate to plot, will be ignored if set bdate (default is 7).',
        type=int
    )
    parser.add_argument(
        '-W', '--width',
        dest='width',
        default=8,
        action='store',
        help='window width.',
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
        print('Default begin:\tsince ' + str(arg.pdays) + ' days ago')

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

    dlimit = []  # date range in human date
    ranepo = []  # date range in epoch
    xlegend = []  # legend to x axis

    # Get datetime objects from dates
    dstart = dateutil.parser.parse(date_limits[0])
    dend = dateutil.parser.parse(date_limits[1])

    # Split time range in days, list with every day
    while dstart <= dend:
        dlimit.append(dstart)
        dstart += timedelta(days=1)
    # Finally add last day time range until midnight
    dlimit.append(dend)

    # Conver to epoch dates, pack two of them, begin and end for each split, and create a list with all
    for reg in range(1, len(dlimit)):
        ranepo.append([int(dlimit[reg-1].timestamp()), int(dlimit[reg].timestamp())])
        xlegend.append(datetime.fromtimestamp(dlimit[reg-1].timestamp()).strftime('%Y-%m-%d'))

    print('Ranges on list:\t' + str(len(ranepo)))

    return(ranepo, xlegend)


def main():
    """Core logic"""

    arg = get_arguments()
    date_limits = date_check(arg)
    date_list, xlegend = date_range(date_limits)

    nran = 0  # Range number
    daysplt = []  # List for all day splits with their events
    max_events = 0  # Max events in a daysplit
    ftmp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv

    # Iterate over each element in (since, until) list
    for nran in range(len(date_list)):
        tsince = str(int(date_list[nran][0]))  # Timestamp arg tsince
        tuntil = str(int(date_list[nran][1]))  # timestamp arg tuntil

        # Query tuptime for every (since, until) and save output to a file
        with open(ftmp, "wb", 0) as out:
            if arg.dbfile:  # If a file is passed, avoid update it
                subprocess.call(["tuptime", "-lsc", "--tsince", tsince, "--tuntil", tuntil, "-f", arg.dbfile, "-n"], stdout=out)
            else:
                subprocess.call(["tuptime", "-lsc", "--tsince", tsince, "--tuntil", tuntil], stdout=out)

        # Get csv file
        daysplit_events = []
        with open(ftmp) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            bad = None  # Register bad shutdown

            for row in csv_reader:
                l_row = []  # List for events in csv rows

                # Control how was the shutdown
                if (row[0] == 'Shutdown') and (row[1] == 'BAD'):
                    bad = True

                # Populate list with (uptime, downtime ok, downtime bad)
                if (row[0] == 'Uptime') or (row[0] == 'Downtime'):

                    if row[0] == 'Uptime':
                        # Add 0 or value to first position
                        l_row.append(int(row[1]))
                    else:
                        l_row.append(0)

                    if row[0] == 'Downtime':
                        # Add (0, value) or (value, 0) to the end
                        if bad is True:
                            l_row.extend((0, int(row[1])))
                        else:
                            l_row.extend((int(row[1]), 0))
                        bad = False  # Reset false
                    else:
                        l_row.extend((0, 0))

                    # Add to events list per day
                    daysplit_events.append(l_row)

            # Finally add all events in a day to daysplt list
            daysplt.append(daysplit_events)

            print('Got range --->\t' + str(nran) + ' with ' + str(len(daysplit_events)) + ' events')

            # Get max number of events between all days
            if len(daysplit_events) > max_events:
                max_events = len(daysplit_events)

    print('Ranges got:\t' + str(len(daysplt)))
    print('Max events:\t' + str(max_events))

    # Convert seconds to days to plot them
    for i in range(0, len(daysplt)):
        for k in range(0, len(daysplt[i])):
            daysplt[i][k][:] = [x / 3600 for x in daysplt[i][k]]

    # For each day...
    for i in range(0, len(daysplt)):

        # All days with equal number of events, fill with 0,0,0
        while max_events >= len(daysplt[i]):
            daysplt[i].append([0, 0, 0])

    # At this poing daysplt have:
    #
    # list_with_days[
    #   list_with_all_events_on_a_day[
    #     list_with_the value_of_each_type_of_event[
    #       uptime, downtime_ok, downtime_bad ]]]

    # Matplotlib requires stack with slices, a list with the elements
    # for all columns from bottom to top:
    #
    # y
    # |  down_bad   down_bad   down_bad
    # |  down_ok    down_ok    down_ok
    # |  uptime     uptime     uptime
    # |  down_bad   down_bad   down_bad
    # |  down_ok    down_ok    down_ok
    # |  uptime     uptime     uptime
    # |----------------------------------x
    # |   day1       day2       dayN

    # Stack events from each day (daysplt) based on their position
    #  [upt, downt ok, downt bad] and so on...
    stack = []
    # for the number of max events present...
    for event in range(0, max_events):

        # ...for each (uptime, downtime ok, downtime bad)...
        for tipe in (0, 1, 2):
            row_stack = []

            # ...for number of days...
            for day in range(0, len(daysplt)):

                # populate value for each day
                row_stack.append(daysplt[day][event][tipe])

            # populate an slice
            stack.append(np.array(row_stack))

    print('Rows to stack:\t' + str(len(stack)))

    ind = np.arange(len(daysplt))    # the x locations for the groups
    width = 0.9
    color_list = ['green', 'grey', 'black']

    plt.figure(figsize=(arg.width, arg.height))

    # Plot events from their position and rotate color
    for i in range(0, len(stack)):
        plt.bar(ind, stack[i], width, color=color_list[i % len(color_list)], linewidth=0, bottom=np.sum(stack[:i], axis=0))

    plt.ylabel('Hours')
    plt.title('Tuptime days bar chart')
    plt.xticks(ind, xlegend, rotation=85, ha="center")
    plt.margins(y=0, x=0.01)
    plt.yticks(np.arange(0, 25, 2))
    plt.grid(color='w', linestyle='--', linewidth=0.5, axis='y')
    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.show()


if __name__ == "__main__":
    main()
