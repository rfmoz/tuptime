#!/usr/bin/env python
# coding: utf-8

import sqlite3
import copy
import argparse
import sys
import logging
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

SECONDS_DAY = 86400


class UptimeRangeInDay:
    # at least 3 splits in each day, represent
    # startup, shutdown and bad shutdown states.
    max_split_count = 3

    def __init__(self, btime, uptime):
        """
        :splits: list, each element is time consumed one of 3 different computer
            state (shutdown, startup, bad shutdown) in same day, the first state
            is always shutdown, then startup, bad shutdown, shutdown...
            But the time consumed on one state can be 0(boot pc at midnight, the
            first element will be 0, as the first state is shutdown)
        :date: date of this startup, if the `btime` and `offtime` of db record
            crossing midnight, it will be split to 2 parts.
        :start_point: start time of this state, changing for different states.
        :end_point: end time of this state.
        :bad_split_idxes: index of bad shutdown state in splits.
        """
        bdate = datetime.fromtimestamp(btime)

        self._splits = []
        self._date = datetime(bdate.year, bdate.month, bdate.day)
        self._start_point = (btime - self._date.timestamp()) / SECONDS_DAY
        self._end_point = self._start_point + uptime / SECONDS_DAY
        self.add_splits((self._start_point,
                        self._end_point - self._start_point, 0))

    @property
    def splits(self):
        return self._splits

    @property
    def date(self):
        return self._date

    @property
    def start_point(self):
        return self._start_point

    @property
    def end_point(self):
        return self._end_point

    @end_point.setter
    def end_point(self, end_point):
        self._end_point = end_point

    @classmethod
    def update_max_split_count(cls, count):
        if count > cls.max_split_count:
            cls.max_split_count = count

    def add_splits(self, split_consumed_times):
        """add time cousumed into splits."""
        self._splits.extend(split_consumed_times)
        self.update_max_split_count(len(self))

    def exchange_splits(self, idx, idy):
        self._splits[idx], self._splits[idy] = \
                self._splits[idy], self._splits[idx]

    def __len__(self):
        return len(self._splits)


def get_uptime_data(arg):
    """Get all rows from database."""

    db_conn = sqlite3.connect(arg.db_file)
    db_conn.row_factory = sqlite3.Row
    conn = db_conn.cursor()
    conn.execute('select rowid as startup, * from tuptime')
    db_rows = conn.fetchall()
    db_conn.close()
    db_rows = [dict(row) for row in db_rows]

    tuptime_install_date = get_last_midnight_date(datetime.fromtimestamp(db_rows[0]['btime']))
    if arg.begin_date < tuptime_install_date:
        logging.warning(f"First tuptime entry was recorded at {tuptime_install_date:%Y-%m-%d}.")

    # last db entry is right now running state
    db_row = db_rows[-1]
    if db_row['offbtime'] == -1:
        db_row['offbtime'] = db_row['btime'] + db_row['uptime']
        db_row['endst'] = 1

    selected_db_rows = []
    # including tuptime record of day before begin_date
    # as last tuptime record may cross midnight
    begin_second = int(arg.begin_date.strftime("%s"))
    end_second = int(arg.end_date.strftime("%s"))

    for db_row in db_rows:
        if db_row['endst'] == 0:  # bad shutdown
            db_row['offbtime'] = int(db_row['offbtime'] + db_row['downtime'])
        if db_row['offbtime'] > begin_second  and  db_row['btime'] < end_second:
            selected_db_rows.append(db_row)

    if len(selected_db_rows) == 0:
        logging.warning("No tuptime entries in this date range.")
        sys.exit(1)

    return selected_db_rows


def get_uptime_range_each_day(selected_db_rows, arg):
    """Get all states for all date between bdate and edate.
    Focus on urid's splits which is a sequence of time consumed on each
    state. The previous state of a startup state must be a shotdown state
    in splits, the next state of a strtup state must be a bad shutdown
    state.
    When way read a new record, we always append 3 type consumed time to
    splits(ordered in shutdown, startup, bad shutdown).
    """

    uptime_ranges = []
    bdate_prev_record = datetime.fromtimestamp(selected_db_rows[0]['btime'])

    def create_or_update_uptime_range():
        """Create uptime range object and insert state
        start/end point to object's splits."""

        nonlocal bdate_prev_record

        if urid.date == bdate_prev_record:
            urid_prev_record = uptime_ranges[-1]
            downtime = urid.start_point - urid_prev_record.end_point
            uptime = urid.end_point - urid.start_point
            badtime = 0
            if entry_state == 0:  # bad shutdown record
                uptime, badtime = badtime, uptime
            urid_prev_record.add_splits((downtime, uptime, badtime))  # badtime
            urid_prev_record.end_point = urid.end_point
        else:
            if entry_state == 0:
                # exchange time consumed between first uptime and first badtime
                urid.exchange_splits(1, 2)
            uptime_ranges.append(urid)
            bdate_prev_record = urid.date

    for db_row in selected_db_rows:
        entry_state = db_row['endst']
        btime = db_row['btime']
        bdate = datetime.fromtimestamp(btime)
        midnight_date = datetime(bdate.year, bdate.month, bdate.day) + timedelta(days=1)
        offbtime = db_row['offbtime']
        while True:
            # split record if corssing midnight
            if offbtime > midnight_date.timestamp():
                urid = UptimeRangeInDay(btime, midnight_date.timestamp() - btime)
                btime = midnight_date.timestamp()
                if urid.date == arg.begin_date - timedelta(days=1):
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

    # last urid index which should set last pc state
    idx_urid = len(uptime_ranges) - 1
    if arg.end_date < datetime.today():
        idx_urid += 1
    # set last pc state to shutdown, if total time of splits less than 1
    for up in uptime_ranges[:idx_urid]:
        total_time = sum(up.splits)
        if abs(1 - total_time) > 1e-3:
            up.add_splits((abs(1 - total_time),))

    if len(uptime_ranges) == 0:
        logging.warning("Computer is running, no other record in this date range in DB.")
        sys.exit(1)

    return uptime_ranges


def plot_time(uptime_ranges, arg):
    """Plot stacked bar chart."""
    max_splits_in_day = UptimeRangeInDay.max_split_count

    # different day got different BAD record, statistic all index that got bad
    # record, insert a 0 to split if that day didn't have a bad record at same
    # split index for all indexes.
    data = [[0] * len(uptime_ranges) for _ in range(max_splits_in_day)]
    for data_col, urid in enumerate(uptime_ranges):
        for data_row, split in enumerate(urid.splits):
            data[data_row][data_col] = split * 24

    bottom_data = copy.deepcopy(data)
    for i in range(1, len(bottom_data)):
        for j in range(len(bottom_data[0])):
            bottom_data[i][j] += bottom_data[i - 1][j]

    fig, ax = plt.subplots()
    fig.set_size_inches(arg.fig_width, arg.fig_height)
    ind = list(range(len(uptime_ranges)))
    width = arg.bar_width

    p1 = ax.bar(ind, data[0], width, color='b')
    p2 = ax.bar(ind, data[1], width, color='r', bottom=data[0])
    p3 = ax.bar(ind, data[2], width, color='k', bottom=data[1])
    colors = {0: 'b', 1: 'r', 2: 'k'}
    for i in range(3, max_splits_in_day):
        region_color = colors[i % 3]
        ax.bar(ind, data[i], width, color=region_color, bottom=bottom_data[i-1])

    ax.set_yticks(list(range(0, 25, 4)))
    ax.set_yticks(list(range(0, 25, 2)), minor=True)
    xticks = [f"{up.date:%Y-%m-%d}" for up in uptime_ranges]
    ax.set_xticks(ind)
    ax.set_xticklabels(xticks, rotation=arg.xtick_labels_rotation)
    ax.set_title("Tuptime bar chart")
    ax.set_ylabel('Hours')
    ax.set_xlabel('Date')
    ax.legend((p1[0], p2[0], p3[0]), ('downtime', 'uptime', 'badtime'), loc="upper right")
    ax.grid(which='minor', axis='y', linestyle=(0, (3, 10, 1, 10)),
            linewidth=arg.line_width, alpha=arg.grid_alpha)
    plt.show()


def get_last_midnight_date(date):
    return datetime.combine(date, datetime.min.time())


def get_arguments():
    DB_FILE = '/var/lib/tuptime/tuptime.db'

    class CustomHelpFormatter(argparse.HelpFormatter):
        def _format_action_invocation(self, action):
            if not action.option_strings or action.nargs == 0:
                return super()._format_action_invocation(action)
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            return ', '.join(action.option_strings) + ' ' + args_string

    parser = argparse.ArgumentParser(formatter_class=lambda prog: CustomHelpFormatter(prog))
    parser.add_argument(
        '-f', '--filedb',
        dest='db_file',
        default=DB_FILE,
        action='store',
        help='database file',
        metavar='FILE'
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
        help='end date to plot, format:Y-m-d. Default edate is today.',
        type=str
    )
    parser.add_argument(
        '-p', '--pastdays',
        dest='past_days',
        default=7,
        action='store',
        help='past days before edate to plot, will be ignored if set bdate (default is 7).',
        type=int
    )
    parser.add_argument(
        '--fwidth',
        dest='fig_width',
        default=10,
        action='store',
        help='figure width.',
        type=int
    )
    parser.add_argument(
        '--fheight',
        dest='fig_height',
        default=12,
        action='store',
        help='figure height.',
        type=int
    )
    parser.add_argument(
        '-w', '--bwidth',
        dest='bar_width',
        default=.5,
        action='store',
        help='width of the bars (default is 0.5).',
        type=float
    )
    parser.add_argument(
        '-r', '--xrotation',
        dest='xtick_labels_rotation',
        default=30,
        action='store',
        help='rotation of xticks label (default is 30 drgrees).',
        type=float
    )
    parser.add_argument(
        '--lwidth',
        dest='line_width',
        default=1,
        action='store',
        help='line width of figure grid (default is 1).',
        type=float
    )
    parser.add_argument(
        '-a', '--galpha',
        dest='grid_alpha',
        default=.0,
        action='store',
        help='alpha value of figure grid (default is 0).',
        type=float
    )

    arg = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s')

    if arg.end_date:
        arg.end_date = datetime.strptime(arg.end_date, "%Y-%m-%d") + timedelta(days=1)
        if arg.end_date > datetime.today() + timedelta(days=1):
            logging.error("end_date can't large than today.")
            sys.exit(-1)
    else:
        arg.end_date = get_last_midnight_date(datetime.today()) + timedelta(days=1)

    if arg.begin_date:
        arg.begin_date = datetime.strptime(arg.begin_date, "%Y-%m-%d")
    else:
        arg.begin_date = arg.end_date - timedelta(days=arg.past_days)

    if arg.begin_date >= arg.end_date:
        logging.error("begin_date must be earlier than end_date.")
        sys.exit(-1)

    return arg


def main():

    arg = get_arguments()
    selected_db_rows = get_uptime_data(arg)
    uptime_ranges = get_uptime_range_each_day(selected_db_rows, arg)
    plot_time(uptime_ranges, arg)


if __name__ == "__main__":
    main()
