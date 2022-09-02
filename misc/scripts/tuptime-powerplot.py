#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sample plot that reports the roughly electric cost per day based on uptime.
It extracts the info from tuptime command execution"""

# Basic usage:
#
# A power consumption of 23 kWh and a kWh cost of 0,66089€:
#
#    $ tuptime-powerplot.py -k 0.66089 23
#
# A power consumption of 55 kWh and a MWh cost of 150€:
#
#    $ tuptime-powerplot.py -m 150 55
#
# A power consumption of 35 kWh, a kWh cost of 0.59$ for last 15 days:
#
#    $ tuptime-powerplot.py -p 15 -k 0.59  35
#
# A power consumption of 40 kWh, a kWh cost of 0.44€ since 1-Jan-2020 to 1-Feb-2020:
#
#    $ tuptime-powerplot.py -k 0.44 -b "01-01-2020" -e "01-02-2020" 40
#
# A power consumption of 40 kWh, a kWh cost of 0.44€ for last 15 days:
#
#    $ tuptime-powerplot.py -k 0.44 -p 15 40
#

from datetime import datetime, timedelta
import subprocess, csv, argparse, tempfile
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser


def get_arguments():
    """Get arguments from command line"""

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        '-b', '--bdate',
        dest='bdate',
        action='store',
        help='begin date to plot, format:"d-m-Y"',
        type=str
    )
    parser.add_argument(
        'consum',
        default=None,
        help='power consumption of the device in Watts / hour',
        metavar='kWh_consumption',
        type=float
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
    group.add_argument(
        '-k', '--kwh',
        dest='kwh',
        default=None,
        action='store',
        help='set price for Kilowatt hour',
        type=float,
        metavar='kWh'
    )
    group.add_argument(
        '-m', '--mwh',
        dest='mwh',
        default=None,
        action='store',
        help='set price for Megawatt hour',
        type=float,
        metavar='MWh'
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
    arg = parser.parse_args()

    if not (arg.kwh or arg.mwh):
        parser.error('Set almost one price for -m (MWh) or -k (kWh)')

    return arg


def date_check(arg):
    """Check and clean dates"""

    # Set user provided or default end date
    if arg.edate:
        end_date = dateutil.parser.parse(arg.edate, dayfirst=True)
    else:
        end_date = datetime.today()
        print('Default end:\tnow')

    # Set user provided or default begind date. Days ago...
    if arg.bdate:
        begin_date = dateutil.parser.parse(arg.bdate, dayfirst=True)
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
        xlegend.append(datetime.fromtimestamp(dlimit[reg-1].timestamp()).strftime('%d-%b-%y'))

    print('Ranges on list:\t' + str(len(ranepo)))

    return(ranepo, xlegend)


def main():
    """Core logic"""

    arg = get_arguments()
    date_limits = date_check(arg)
    date_list, xlegend = date_range(date_limits)

    # Set price for Watts per second
    if arg.mwh:
        arg.kwh = arg.mwh / 1000
    wth = arg.kwh / 1000
    wts = wth / 3600
    consum = arg.consum

    days = []  # List for day values
    ftmp = tempfile.NamedTemporaryFile().name  # File to store Tuptime csv

    # Iterate over each element in (since, until) list
    for nran, _  in enumerate(date_list):
        tsince = str(int(date_list[nran][0]))  # Timestamp arg tsince
        tuntil = str(int(date_list[nran][1]))  # timestamp arg tuntil

        # Query tuptime for every (since, until) and save output into a file
        with open(ftmp, "wb", 0) as out:
            if arg.dbfile:  # If a file is passed, avoid update it
                subprocess.call(["tuptime", "-lsc", "--tsince", tsince, "--tuntil", tuntil, "-f", arg.dbfile, "-n"], stdout=out)
            else:
                subprocess.call(["tuptime", "-lsc", "--tsince", tsince, "--tuntil", tuntil], stdout=out)

        # Parse csv file
        with open(ftmp) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            uptimes = []  # Uptime events in csv rows
            for row in csv_reader:

                # Populate list with all uptimes inside each day
                if row[0] == 'Uptime':
                    uptimes.append(int(row[1]))

            # Populate with total price calculation
            days.append(sum(uptimes) * wts * consum)

            print(str(nran) + ' range --->\t' + str(sum(uptimes)) + 's - ' + str(days[-1]))

    print('Ranges got:\t' + str(len(days)))
    print('Power cons.:\t' + str(consum) + ' kWh')
    print('kWh price:\t' + str(arg.kwh))
    print('Total cost:\t' + str(round(sum(days), 2)))

    # Create plot

    ind = np.arange(len(days))  # number of days on x

    plt.figure(figsize=((arg.width / 2.54), (arg.height / 2.54)))  # Set values from inches to cm
    plt.title('Roughly Electric Cost per Day')
    plt.figtext(0.005, 0.005, "Total: " + str(round(sum(days), 2)), weight=1000)

    plt.bar(ind, days, color='steelblue')
    #plt.plot(ind, days, linewidth=2, marker='o', color='forestgreen')

    plt.grid(color='lightblue', linestyle='--', linewidth=0.5, axis='x')
    plt.xticks(ind, xlegend)
    plt.gcf().autofmt_xdate()
    plt.ylabel('Cost in currency')
    plt.margins(y=0.01, x=0.01)
    plt.grid(color='lightgrey', linestyle='--', linewidth=0.5, axis='y')
    plt.tight_layout()
    cfig = plt.get_current_fig_manager()
    cfig.canvas.set_window_title("Tuptime")
    plt.show()


if __name__ == "__main__":
    main()
