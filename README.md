tuptime
=======

[![License](https://img.shields.io/github/license/rfmoz/tuptime)](https://github.com/rfmoz/tuptime/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/rfmoz/tuptime)](https://github.com/rfmoz/tuptime/releases)
[![Python](https://img.shields.io/badge/python-3-blue)](https://www.python.org/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/rfmoz/tuptime)

Tuptime reports historical and statistical system uptime, preserved across reboots. Like uptime, but with extended information.


### Sample output

Just after install:

	System startups:        1  since  24/09/15 21:54:09
	System shutdowns:       0 ok  +  0 bad
	System life:            21m 30s

	Longest uptime:         21m 30s  from  24/09/15 21:54:09
	Average uptime:         21m 30s
	System uptime:          100.0%  =  21m 30s

	Longest downtime:	0s
	Average downtime:       0s
	System downtime:        0.0%  =  0s

	Current uptime:         21m 30s  since  24/09/15 21:54:09

A few days later:

	System startups:        110  since  08/08/15 10:15:27
	System shutdowns:       107 ok  +  2 bad
	System life:            47d 12h 02m 15s

	Longest uptime:         2h 10m 44s  from  09/08/15 20:49:17
	Average uptime:         25m 08s
	System uptime:          4.04%  =  1d 22h 04m 44s

	Longest downtime:	7d 10h 17m 26s  from  10/08/15 06:09:45
	Average downtime:       9h 56m 42s
	System downtime:        95.96%  =  45d 13h 57m 30s

	Current uptime:         23m 33s  since  24/09/15 21:54:09

Switch to -t | --table option:

	No.        Startup T.        Uptime         Shutdown T.   End    Downtime
                                                                                                                                    
	1   08/08/15 10:15:27           42s   08/08/15 10:16:09    OK         16s
	2   08/08/15 10:16:26           49s   08/08/15 10:17:15    OK         16s
	3   08/08/15 10:17:32        5m 47s   08/08/15 10:23:19    OK         16s
	4   08/08/15 10:23:36            9s   08/08/15 10:23:45   BAD         42s
	5   08/08/15 10:24:28    2h 09m 27s   08/08/15 12:33:55    OK     41m 44s
        . . .

Or switch to -l | --list option:

	Startup:  1  at  08/08/15 10:15:27
	Uptime:   42s
	Shutdown: OK  at  08/08/15 10:16:09
	Downtime: 16s

	Startup:  2  at  08/08/15 10:16:26
	Uptime:   49s
	Shutdown: OK  at  08/08/15 10:17:15
	Downtime: 16s

	Startup:  3  at  08/08/15 10:17:32
	Uptime:   5m 47s
	Shutdown: OK  at  08/08/15 10:23:19
	Downtime: 16s
	. . .


### Basic Installation


#### By package manager

* Debian: https://packages.debian.org/tuptime
* Ubuntu: https://packages.ubuntu.com/tuptime
* Fedora, EPEL: https://src.fedoraproject.org/rpms/tuptime
* FreeBSD: https://www.freshports.org/sysutils/tuptime
* Archlinux: https://aur.archlinux.org/packages/tuptime
* OpenSUSE: https://software.opensuse.org/package/tuptime (Community Maintained / Unofficial)
* Alpine: https://pkgs.alpinelinux.org/package/edge/testing/x86_64/tuptime

#### By one-liner script

	bash < <(curl -Ls https://git.io/tuptime-install.sh)


#### By manual method

Briefly in a Linux or FreeBSD system...

Clone the repo:

	git clone --depth=1 https://github.com/rfmoz/tuptime.git

Copy the 'tuptime' file located under 'tuptime/src/' directory to '/usr/bin/' and make it executable:

	cp tuptime/src/tuptime /usr/bin/tuptime
	chmod ugo+x /usr/bin/tuptime

Ensure that the system passes the prerequisites:

	Python 3

Run first with a privileged user:

	tuptime

Pick from 'src/' folder the right file for your cron and init manager, setup both
properly. See 'tuptime-manual.txt' for more information.


### Highlights about Tuptime internals

- It doesn't run as a daemon, at least, it only needs execution when the init manager startup and shutdown the system. To avoid issues with a switch off without a proper shutdown, like power failures, a cron job and a .timer unit are shipped with the project to update the registers each n minutes. As a system administrator, you can easily choose the best number for your particular system requirements.

- It is written in Python using common modules and as few as possible, quick execution, easy to see what is inside it, and modify it to fit for your particular use case.

- It registers the times in a sqlite database. Any other software can use it. The specs are in the tuptime-manual.txt. Also, it has the option to output the registers in seconds and epoch or/and in csv format, easy to pipe it to other commands.

- Its main purpose is tracking all the system startups/shutdowns and present that information to the user in a more understandable way. It doesn't have mail alerts when milestones are reached or the limitation of keeping the last n records.

- It's written to avoid false startups registers. This is an issue that sometimes happens when the NTP adjust the system clock, on virtualized environments, on servers with high load, when the system resynchronizes with its RTC clock after a suspend and resume cycle...

- It can report:
  - Registers as a table or list ordering by any label.
  - The whole life of the system or only a part of it, closing the range between startups/shutdowns or timestamps.
  - Accumulated running and sleeping time over an uptime.
  - The kernel version used and boot identifiers.
  - The system state at specific point in time.


### Alternatives

journalctl --list-boots - Show a tabular list of boot numbers (relative to the current boot), their IDs, and the timestamps of the first and last message pertaining to the boot. Closer output than 'tuptime  -bit'.
https://github.com/systemd/systemd/

uptimed - Uptime record daemon keeping track of the highest uptimes a computer system ever had. It uses the system boot time to keep sessions apart from each other.
https://github.com/rpodgorny/uptimed

downtimed - Monitoring operating system downtime, uptime, shutdowns and crashes and for keeping record of such events.
https://dist.epipe.com/downtimed/

lastwake - Analyzes the system journal and prints out wake-up and sleep timestamps; for each cycle it tells whether the system was suspended to RAM or to disk (hibernated).
https://github.com/arigit/lastwake.py

(bonus) dateutils - Not an alternative, but it is a nifty collection of tools to work with dates.
https://github.com/hroptatyr/dateutils

ruptime - Is a modern rwhod replacement that is easy to customize, not limited to a network, and does not send clear text data over the network.
https://github.com/alexmyczko/ruptime


### More information

Please, read tuptime-manual.txt for a complete reference guide.

DeepWiki: https://deepwiki.com/rfmoz/tuptime
