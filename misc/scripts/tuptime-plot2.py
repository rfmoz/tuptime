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
    begin_date = begin_date.replace(hour=0, minute=0, second=0).strftime("%d-%b-%Y %H:%M:%S")
    end_date = end_date.replace(hour=23, minute=59, second=59).strftime("%d-%b-%Y %H:%M:%S")

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

        # From datetime, get only hour
        for elem in tst['up']: pie['up'].append(str(elem.hour))
        for elem in tst['down']: pie['down'].append(str(elem.hour))

        # Count elements on list or set '0' if emtpy. Get list with items
        pie['up'] = dict(Counter(pie['up'])).items() if pie['up'] else [('0', 0)]
        pie['down'] = dict(Counter(pie['down'])).items() if pie['down'] else [('0', 0)]

        # Values ordered by first element on list that was key on source dict
        pie['up'] = sorted(pie['up'], key=lambda ordr: int(ordr[0]))
        pie['down'] = sorted(pie['down'], key=lambda ordr: int(ordr[0]))

        # Set two plots and their frame size
        _, axs = plt.subplots(1, 2, figsize=((arg.width / 2.54), (arg.height / 2.54)))

        # Set values for each pie plot
        axs[0].pie([v[1] for v in pie['up']], labels=[k[0].rjust(2, '0') + str('h') for k in pie['up']],
                   autopct=lambda p : '{:.1f}%\n{:,.0f}'.format(p,p * sum([v[1] for v in pie['up']])/100),
                   startangle=90, counterclock=False,
                   textprops={'fontsize': 8}, wedgeprops={'alpha':0.85})
        axs[0].set(aspect="equal", title='Startup')

        axs[1].pie([v[1] for v in pie['down']], labels=[str(k[0]).rjust(2, '0') + str('h') for k in pie['down']],
                   autopct=lambda p : '{:.1f}%\n{:,.0f}'.format(p,p * sum([v[1] for v in pie['down']])/100),
                   startangle=90, counterclock=False,
                   textprops={'fontsize': 8}, wedgeprops={'alpha':0.85})
        axs[1].set(aspect="equal", title='Shutdown')

        axs[0].text(1, -0.1, str('From    ' + str(date_limits[0]) + '    to    ' + str(date_limits[1])), size=10, ha="center", transform=axs[0].transAxes)
        plt.suptitle("Events per Hours in all Days", fontsize=14)

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
        plt.scatter(scatt_x['up'], scatt_y['up'], s=200, color='forestgreen', edgecolors='white', alpha=0.85, marker="X", label='Up')
        plt.scatter(scatt_x['down_ok'], scatt_y['down_ok'], s=200, color='grey', edgecolors='white', alpha=0.85, marker="X", label='Down ok')
        plt.scatter(scatt_x['down_bad'], scatt_y['down_bad'], s=200, color='black', edgecolors='white', alpha=0.85, marker="X", label='Down bad')

        # Format axes:
        plt.gcf().autofmt_xdate()
        axs = plt.gca()

        #  X as days and defined limits with their margin
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
        axs.xaxis.set_major_locator(mdates.DayLocator())
        plt.xlim(datetime.strptime(date_limits[0], '%d-%b-%Y %H:%M:%S') - timedelta(hours=4),
                 datetime.strptime(date_limits[1], '%d-%b-%Y %H:%M:%S') - timedelta(hours=20))

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
