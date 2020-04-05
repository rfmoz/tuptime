#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sample plot with hours per every state in each day
from the info that the tuptime command report"""


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
        default=6,
        action='store',
        help='window height',
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
        default=8,
        action='store',
        help='window width',
        type=int
    )
    arg = parser.parse_args()
    return arg


def date_check(arg):
    """Check and clean dates"""

    # Set user or default end date.
    if arg.edate:
        end_date = dateutil.parser.parse(arg.edate)
    else:
        end_date = datetime.today()
        print('Default end:\tnow')

    # Set user or default begind date. Days ago...
    if arg.bdate:
        begin_date = dateutil.parser.parse(arg.bdate)
    else:
        begin_date = end_date - timedelta(days=arg.pdays)
        print('Default begin:\tsince ' + str(arg.pdays) + ' days ago')


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
    ftmp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv

    # Iterate over each element in (since, until) list
    for nran, _  in enumerate(date_list):
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

    print('Ranges got:\t' + str(len(daysplt)))

    # At this poing daysplt have:
    #
    # list_with_days[
    #   list_with_all_events_on_a_day[
    #     list_with_the value_of_each_type_of_event[
    #       uptime, downtime_ok, downtime_bad ]]]

    # For each day, get total value for each type of event and convert seconds to hours
    for i in range(0, len(daysplt)):
        daysplt[i] = [(sum(j) / 3600) for j in zip(*daysplt[i])]

    # At this poing daysplt have:
    #
    # list_with_days[
    #   list_with_total_time of_each_type_of_event[
    #     uptime, downtime_ok, downtime_bad ]]

    # Matplotlib requires stack with slices
    #
    # y
    # |  uptime     uptime     uptime
    # |  down_ok    down_ok    down_ok
    # |  down_bad   down_bad   down_bad
    # |----------------------------------x
    # |   day1       day2       dayN

    # Get each state values slice from each day
    days = {'uptime': [], 'down_ok': [], 'down_bad': []}
    for i in daysplt:
        if not i: i = [0, 0, 0]  # Set empty
        days['uptime'].append(i[0])
        days['down_ok'].append(i[1])
        days['down_bad'].append(i[2])

    ind = np.arange(len(daysplt))  # number of days on x

    plt.figure(figsize=(arg.width, arg.height))

    # Old bar plot
    #width = 0.9  # column size
    #plt.bar(ind, days['uptime'], width, color='green', label='Uptime')
    #plt.bar(ind, days['down_ok'], width, color='grey', label='Downtime OK', bottom=days['uptime'])
    #plt.bar(ind, days['down_bad'], width, color='black', label='Downtime BAD', bottom=[i+j for i, j in zip(days['uptime'], days['down_ok'])])

    plt.plot(ind, days['uptime'], linewidth=2, marker='o', color='green', label='Uptime')
    plt.plot(ind, days['down_ok'], linewidth=2, marker='o', color='grey', label='Down Ok')
    plt.plot(ind, days['down_bad'], linewidth=2, marker='o', color='black', label='Down Bad')

    plt.ylabel('Hours')
    plt.title('Hours per State by Day')
    plt.xticks(ind, xlegend, rotation=85, ha="center")
    plt.margins(y=0, x=0.01)
    plt.yticks(np.arange(0, 25, 2))
    plt.ylim(top=26)
    plt.grid(color='lightgrey', linestyle='--', linewidth=0.5, axis='y')
    plt.grid(color='lightblue', linestyle='--', linewidth=0.5, axis='x')
    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
