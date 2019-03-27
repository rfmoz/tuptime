#!/usr/bin/env python
# coding: utf-8

import sqlite3
import copy
import argparse
import sys
import logging
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class UptimeRangeInDay:

    def __init__(self, btime, uptime):
        """
        :splits: list, each element is time spent of 2 different computer state
            (shutdown, startup) in same day, the first state is always shutdown,
            then startup, shutdown, startup...
            But the time spent on one state can be 0(boot pc at midnight, the
            first element will be 0, as the first state is shutdown)
        :day: date of this startup, if the `btime` and `offtime` of db record
            crossing midnight, it will be split to 2 parts.
        :start_point: start time of this state, changing for different states.
        :end_point: end time of this state.
        """
        self.splits = []
        bdate = datetime.fromtimestamp(btime)
        self.date = datetime(bdate.year, bdate.month, bdate.day)
        self.start_point = (btime - self.date.timestamp()) / 86400
        self.end_point = self.start_point + uptime / 86400
        self.splits.append(self.start_point)
        self.splits.append(self.end_point - self.start_point)


def get_uptime_data(arg):
    """Get all rows from database."""

    db_conn = sqlite3.connect(arg.db_file)
    db_conn.row_factory = sqlite3.Row
    conn = db_conn.cursor()
    conn.execute('select rowid as startup, * from tuptime')
    db_rows = conn.fetchall()
    db_conn.close()
    db_rows = [dict(row) for row in db_rows[:-1]]

    if arg.set_date:
        tuptime_install_date = get_last_midnight_date(datetime.fromtimestamp(db_rows[0]['btime']))
        if arg.begin_date < tuptime_install_date:
            logging.warning(f"First tuptime entry was recorded at {tuptime_install_date:%Y-%m-%d}.")

        db_date_rows = []
        # including tuptime record of day before begin_date
        # as last tuptime record may cross midnight
        begin_second = int(arg.begin_date.strftime("%s")) - 86400
        end_second = int(arg.end_date.strftime("%s"))

        for row in db_rows:
            if begin_second <= row['btime'] < end_second:
                db_date_rows.append(row)

        if len(db_date_rows) == 0:
            logging.warning("No tuptime entries in this date range.")
            sys.exit(1)
        return db_date_rows

    return db_rows


def get_uptime_range_each_day(db_rows, arg):
    """Get all states for all date after `tuptime` installed."""

    uptime_ranges = []
    max_splits_in_day = 2
    bdate_prev_record = datetime.fromtimestamp(db_rows[0]['btime'])
    record_before_begin_date = True

    def create_or_update_uptime_range():
        """Create uptime range object and insert state start/end point to object's splits."""

        nonlocal uptime_ranges, max_splits_in_day, bdate_prev_record, urid

        if urid.date == bdate_prev_record:
            urid_prev_record = uptime_ranges[-1]
            urid_prev_record.splits.append(urid.start_point - urid_prev_record.end_point)
            urid_prev_record.splits.append(urid.end_point - urid.start_point)
            urid_prev_record.end_point = urid.end_point
            if len(urid_prev_record.splits) > max_splits_in_day:
                max_splits_in_day = len(urid_prev_record.splits)
        else:
            uptime_ranges.append(urid)
            bdate_prev_record = urid.date

    for db_row in db_rows:
        btime = db_row['btime']
        bdate = datetime.fromtimestamp(btime)
        midnight_date = datetime(bdate.year, bdate.month, bdate.day) + timedelta(days=1)
        offbtime = db_row['offbtime']
        if arg.set_date and record_before_begin_date:
            if datetime.fromtimestamp(offbtime) < arg.begin_date:
                continue
            else:
                record_before_begin_date = False
        while True:
            # split record if corssing midnight
            if offbtime > midnight_date.timestamp():
                urid = UptimeRangeInDay(btime, midnight_date.timestamp() - btime)
                btime = midnight_date.timestamp()
                if arg.set_date and urid.date == arg.begin_date - timedelta(days=1):
                    continue
                create_or_update_uptime_range()
                # break, otherwise will cross end_date
                if midnight_date == arg.end_date:
                    break
                midnight_date += timedelta(days=1)
            else:
                urid = UptimeRangeInDay(btime, offbtime - btime)
                create_or_update_uptime_range()
                break

    # last urid index which ignored to add last pc state
    idx_urid = len(uptime_ranges) - 1
    if  arg.set_date and arg.end_date < datetime.today():
        idx_urid += 1
    # add last pc state to shutdown, if total time of splits less than 1
    for up in uptime_ranges[:idx_urid]:
        total_time = sum(up.splits)
        if abs(1 - total_time) > 1e-3:
            up.splits.append(abs(1 - total_time))

    return uptime_ranges, max_splits_in_day


def plot_time(uptime_ranges, max_splits_in_day, arg):
    """Plot stacked bar chart."""

    if arg.set_date:
        arg.past_days = len(uptime_ranges)
    else:
        if arg.past_days > len(uptime_ranges):
            arg.past_days = len(uptime_ranges)
        uptime_ranges = uptime_ranges[-arg.past_days:]

    xticks = [f"{up.date:%Y%m%d}" for up in uptime_ranges]

    data = []
    for i in range(max_splits_in_day):
        data.append([])
        for j in range(arg.past_days):
            if i < len(uptime_ranges[j].splits):
                data[i].append(uptime_ranges[j].splits[i] * 24)
            else:
                data[i].append(0)

    bottom_data = copy.deepcopy(data)
    for i in range(1, len(bottom_data)):
        for j in range(len(bottom_data[0])):
            bottom_data[i][j] += bottom_data[i - 1][j]

    plt.figure(figsize=(arg.fig_length, arg.fig_width))
    ind = list(range(len(uptime_ranges)))
    width = arg.bar_width

    p1 = plt.bar(ind, data[0], width, color='b')
    p2 = plt.bar(ind, data[1], width, color='r', bottom=data[0])
    for i in range(2, max_splits_in_day):
        if i % 2 == 0:
            region_color = 'b'
        else:
            region_color = 'r'
        plt.bar(ind, data[i], width, color=region_color, bottom=bottom_data[i-1])

    plt.xticks(ind, xticks)
    plt.yticks(list(range(0, 25, 2)))
    plt.title("Tuptime bar chart")
    plt.ylabel('Hours')
    plt.xlabel('Date')
    plt.legend((p1[0], p2[0]), ('downtime', 'uptime'))
    plt.show()


def get_last_midnight_date(date):
    return datetime.combine(date, datetime.min.time())


def get_arguments():
    DB_FILE = '/var/lib/tuptime/tuptime.db'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--filedb',
        dest='db_file',
        default=DB_FILE,
        action='store',
        help='database file',
        metavar='FILE'
    )
    parser.add_argument(
        '-l', '--flength',
        dest='fig_length',
        default=12,
        action='store',
        help='figure length',
        type=int
    )
    parser.add_argument(
        '-w', '--fwidth',
        dest='fig_width',
        default=10,
        action='store',
        help='figure width',
        type=int
    )
    parser.add_argument(
        '-bw', '--bwidth',
        dest='bar_width',
        default=.5,
        action='store',
        help='The width of the bars (default is 0.5).',
        type=float
    )
    parser.add_argument(
        '-b', '--bdate',
        dest='begin_date',
        action='store',
        help='begin date to plot, format:Y-m-d.',
        type=str
    )
    parser.add_argument(
        '-e', '--edate',
        dest='end_date',
        action='store',
        help='end date to plot, format:Y-m-d. If bdate has been set, default edate is today.',
        type=str
    )
    parser.add_argument(
        '-p', '--pastdays',
        dest='past_days',
        default=7,
        action='store',
        help='past days to plot, will be ignored if set bdate (default is 7).',
        type=int
    )

    arg = parser.parse_args()
    if arg.begin_date:
        arg.begin_date = datetime.strptime(arg.begin_date, "%Y-%m-%d")

        if arg.end_date:
            arg.end_date = datetime.strptime(arg.end_date, "%Y-%m-%d") + timedelta(days=1)
            if arg.end_date > datetime.today() + timedelta(days=1):
                logging.error("end_date can't large than today.")
                sys.exit(-1)
        else:
            arg.end_date = get_last_midnight_date(datetime.today()) + timedelta(days=1)

        if arg.begin_date >= arg.end_date:
            logging.error("begin_date can't large than end_date.")
            sys.exit(-1)
        arg.set_date = True
    else:
        arg.set_date = False

    return arg


def main():

    arg = get_arguments()
    db_rows = get_uptime_data(arg)
    uptime_ranges, max_splits_in_day = get_uptime_range_each_day(db_rows, arg)
    plot_time(uptime_ranges, max_splits_in_day, arg)


if __name__ == "__main__":
    main()
