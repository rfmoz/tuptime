#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sample plot that reports the number of hours/events per every state
in each day. It extracts the info from tuptime command execution"""


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
        help='begin date to plot, format:"d-m-Y"',
        type=str
    )
    parser.add_argument(
        '-e', '--edate',
        dest='edate',
        action='store',
        help='end date to plot, format:"d-m-Y" (default today)',
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
        help='window height in cm (default 13)',
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
        help='window width in cm (default 17)',
        type=int
    )
    parser.add_argument(
        '-x',
        dest='report_events',
        action='store_true',
        default=False,
        help='swich to report startup/shutdown events instead of hours'
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
    begin_date = begin_date.replace(hour=0, minute=0, second=0).strftime("%d-%b-%Y %H:%M:%S")
    end_date = end_date.replace(hour=23, minute=59, second=59).strftime("%d-%b-%Y %H:%M:%S")

    print('Begin datetime:\t' + str(begin_date))
    print('End datetime:\t' + str(end_date))

    return([begin_date, end_date])


def date_range(date_limits):
    """Get the range of dates to apply"""

    dlimit = []  # date range in human date
    ranepo = []  # date range in epoch
    xlegend = []  # legend to x axis

    # Get datetime objects from dates
    dstart = dateutil.parser.parse(date_limits[0])
    dend = dateutil.parser.parse(date_limits[1])

    # Split time range in days
    while dstart <= dend:
        dlimit.append(dstart)
        dstart += timedelta(days=1)
    dlimit.append(dend)  # Finally add last day time range until midnight

    # Convert to epoch dates, pack two of them, begin and end for each split, and create a list with all
    for reg in range(1, len(dlimit)):
        ranepo.append([int(dlimit[reg-1].timestamp()), int(dlimit[reg].timestamp())])
        xlegend.append(datetime.fromtimestamp(dlimit[reg-1].timestamp()).strftime('%d-%b-%Y'))

    print('Ranges on list:\t' + str(len(ranepo)))

    return(ranepo, xlegend)


def main():
    """Core logic"""

    arg = get_arguments()
    date_limits = date_check(arg)
    date_list, xlegend = date_range(date_limits)

    daysplt = []  # List for all day splits with their events
    ftmp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv
    shutst = None

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

        # Parse csv file
        daysplit_events = []
        with open(ftmp) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                l_row = [0, 0, 0]  # Events in csv rows

                # Control how was the shutdown
                if row[0] == 'Shutdown':
                    if row[1] == 'BAD': shutst = 'BAD'
                    if row[1] == 'OK': shutst = 'OK'

                if arg.report_events:
                    # Populate list with (startup, shutdown ok, shutdown bad)
                    if ((row[0] == 'Startup') or (row[0] == 'Shutdown')) and len(row) > 2:

                        if row[0] == 'Startup' and row[2] == 'at':
                            l_row[0] = 1

                        if row[0] == 'Shutdown' and row[2] == 'at':
                            if shutst == 'BAD':
                                l_row[2] = 1
                            else:
                                l_row[1] = 1

                else:
                    # Populate list with (uptime, downtime ok, downtime bad)
                    if (row[0] == 'Uptime') or (row[0] == 'Downtime'):

                        if row[0] == 'Uptime':
                            l_row[0] = int(row[1])

                        if row[0] == 'Downtime':
                            if shutst == 'BAD':
                                l_row[2] = int(row[1])
                            else:
                                l_row[1] = int(row[1])

                # Add to events list per day
                daysplit_events.append(l_row)

            print(str(nran) + ' range --->\t' + str(len([i for i in daysplit_events if i != [0, 0, 0]])) + ' events')

            # Per day, get total value for each type of event
            if arg.report_events:
                daysplit_events = [(sum(j)) for j in zip(*daysplit_events)]
            else:
                # Convert seconds to hours
                daysplit_events = [(sum(j) / 3600) for j in zip(*daysplit_events)]

            # Populate daysplt list with totals
            daysplt.append(daysplit_events)

    print('Ranges got:\t' + str(len(daysplt)))

    # At this point daysplt have one of these:
    #
    # list_with_days[
    #   list_with_total_time of_each_type_of_event[
    #     uptime, downtime_ok, downtime_bad ]]
    #
    # list_with_days[
    #   list_with_total_counter of_each_type_of_event[
    #     startup, shutdown_ok, shutdown_bad ]]

    # Matplotlib requires stack with slices
    #
    # y
    # |  up         up         up
    # |  down_ok    down_ok    down_ok
    # |  down_bad   down_bad   down_bad
    # |----------------------------------x
    # |   day1       day2       dayN

    # Get each state values slice from each day
    days = {'up': [], 'down_ok': [], 'down_bad': []}
    for i in daysplt:
        days['up'].append(i[0])
        days['down_ok'].append(i[1])
        days['down_bad'].append(i[2])

    ind = np.arange(len(daysplt))  # number of days on x

    # Set width and height from inches to cm
    plt.figure(figsize=((arg.width / 2.54), (arg.height / 2.54)))

    if arg.report_events:
        plt.ylabel('Events')
        plt.title('Events per state by Day')
        maxv = max(i for v in days.values() for i in v)  # Get max value on all ranges
        plt.yticks(np.arange(0, (maxv + 1), 1))
        plt.ylim(top=(maxv + 1))
        rlabel = ['Startup', 'Shutdown Ok', 'Shutdown Bad']
        width = 0.42  # column size

        # Set position of bar on X axis
        pst1 = np.arange(len(ind))
        pst2 = [x + width for x in pst1]

        plt.bar(pst1, days['up'], width, color='forestgreen', label=rlabel[0], edgecolor='white')
        plt.bar(pst2, days['down_ok'], width, color='grey', label=rlabel[1], edgecolor='white', bottom=days['down_bad'])
        plt.bar(pst2, days['down_bad'], width, color='black', label=rlabel[2], edgecolor='white')

        ind = ind + width / 2

    else:
        plt.ylabel('Hours')
        plt.title('Hours per State by Day')
        plt.yticks(np.arange(0, 25, 2))
        plt.ylim(top=26)
        rlabel = ['Uptime', 'Downtime']

        # Merge all downtimes
        days['down'] = [x + y for x, y in zip(days['down_ok'], days['down_bad'])]

        # Old bar plot
        #width = 0.9  # column size
        #plt.bar(ind, days['up'], width, color='forestgreen', label=rlabel[0])
        #plt.bar(ind, days['down'], width, color='grey', label=rlabel[1], bottom=days['up'])

        plt.plot(ind, days['up'], linewidth=2, marker='o', color='forestgreen', label=rlabel[0])
        plt.plot(ind, days['down'], linewidth=2, marker='o', color='grey', linestyle='--', label=rlabel[1])

        plt.grid(color='lightblue', linestyle='--', linewidth=0.5, axis='x')

    plt.xticks(ind, xlegend)
    plt.gcf().autofmt_xdate()
    plt.margins(y=0, x=0.01)
    plt.grid(color='lightgrey', linestyle='--', linewidth=0.5, axis='y')
    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
