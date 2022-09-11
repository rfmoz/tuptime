tuptime
=======

Tuptime is a tool for report the historical and statistical real time of the system, keeping it between restarts. Like uptime command but with more interesting output.


### Sample output

Just after install:

	System startups:        1  since  21:54:09 24/09/15
	System shutdowns:       0 ok  +  0 bad
	System life:            21m 30s

	Longest uptime:         21m 30s  from  21:54:09 24/09/15
	Average uptime:         21m 30s
	System uptime:          100.0%  =  21m 30s

	Longest downtime:	0s
	Average downtime:       0s
	System downtime:        0.0%  =  0s

	Current uptime:         21m 30s  since  21:54:09 24/09/15

A few days later:

	System startups:        110  since  10:15:27 08/08/15
	System shutdowns:       107 ok  +  2 bad
	System life:            47d 12h 2m 15s

	Longest uptime:         2h 10m 44s  from  20:49:17 09/08/15
	Average uptime:         25m 8s
	System uptime:          4.04%  =  1d 22h 4m 44s

	Longest downtime:	7d 10h 17m 26s  from  06:09:45 10/08/15
	Average downtime:       9h 56m 42s
	System downtime:        95.96%  =  45d 13h 57m 30s

	Current uptime:         23m 33s  since  21:54:09 24/09/15

Swich to -t | --table option:

	No.        Startup T.        Uptime         Shutdown T.   End    Downtime
                                                                                                                                    
	1   10:15:27 08/08/15           42s   10:16:09 08/08/15    OK         16s
	2   10:16:26 08/08/15           49s   10:17:15 08/08/15    OK         16s
	3   10:17:32 08/08/15        5m 47s   10:23:19 08/08/15    OK         16s
	4   10:23:36 08/08/15            9s   10:23:45 08/08/15   BAD         42s
	5   10:24:28 08/08/15     2h 9m 27s   12:33:55 08/08/15    OK     41m 44s
        . . .

Or swich to -l | --list option:

	Startup:  1  at  10:15:27 08/08/15
	Uptime:   42s
	Shutdown: OK  at  10:16:09 08/08/15
	Downtime: 16s

	Startup:  2  at  10:16:26 08/08/15
	Uptime:   49s
	Shutdown: OK  at  10:17:15 08/08/15
	Downtime: 16s

	Startup:  3  at  10:17:32 08/08/15
	Uptime:   5m 47s
	Shutdown: OK  at  10:23:19 08/08/15
	Downtime: 16s
	. . .


### Basic Installation


#### By package manager

* Debian: https://packages.debian.org/tuptime
* Ubuntu: https://packages.ubuntu.com/tuptime
* Fedora, EPEL: https://src.fedoraproject.org/rpms/tuptime
* FreeBSD: https://www.freshports.org/sysutils/tuptime


#### By one-liner script

	bash < <(curl -Ls https://git.io/tuptime-install.sh)


#### By manual method

Briefly in a Linux or FreeBSD system...

Clone the repo:

	git clone --depth=1 https://github.com/rfmoz/tuptime.git

Copy the 'tuptime' file located under 'latest/' directory to '/usr/bin/' and make it executable:

	cp tuptime/src/tuptime /usr/bin/tuptime
	chmod ugo+x /usr/bin/tuptime

Assure that the system pass the prerequisites:

	python 3.X 

Run first with a privileged user:

	tuptime

Pick from 'src/' folder the right file for your cron and init manager, setup both
properly. See 'tuptime-manual.txt' for more information.


### Highlights about Tuptime internals

- It doesn't run as a daemon, at least, it only needs execution when the init manager startup and shutdown the system. To avoid issues with a switch off without a proper shutdown, like power failures, a cron job and a .timer unit are shipped with the project to update the registers each n minutes. As a system administrator, you can easily choose the best number for your particular system requirements.

- It is written in Python using common modules and as few as possible, quick execution, easy to see what is inside it, and modify it for fit for your particular use case.

- It registers the times in a sqlite database. Any other software can use it. The specs are in the tuptime-manual.txt. Also, it has the option to output the registers in seconds and epoch or/and in csv format, easy to pipe it to other commands.

- Its main purpose is tracking all the system startups/shutdowns and present that information to the user in a more understandable way. Don't have mail alerts when a milestones are reached or the limitation of keep the last n records.

- It's written to avoid false startups registers. This is an issue that sometimes happens when the NTP adjust the system clock, on virtualized environments, on servers with high load, when the system resynchronized with their RTC clock after a suspend and resume cycle...

- It can report:
  - Registers as a table or list ordering by any label.
  - The whole life of the system or only a part of it, closing the range between startups/shutdowns or timestamps.
  - Accumulated running and sleeping time over an uptime.
  - The kernel version used and boot idenfiers.
  - The system state at specific point in time.


### Alternatives

journalctl --list-boots - Show a tabular list of boot numbers (relative to the current boot), their IDs, and the timestamps of the first and last message pertaining to the boot. Close output than 'tuptime  -bit'.
https://github.com/systemd/systemd/

uptimed - Is an uptime record daemon keeping track of the highest uptimes a computer system ever had. It uses the system boot time to keep sessions apart from each other.
https://github.com/rpodgorny/uptimed

downtimed - Is a program for monitoring operating system downtime, uptime, shutdowns and crashes and for keeping record of such events.
https://dist.epipe.com/downtimed/

lastwake - Analyzes the system journal and prints out wake-up and sleep timestamps; for each cycle it tells whether the system was suspended to RAM or to disk (hibernated).
https://github.com/arigit/lastwake.py

(bonus) dateutils - Not an alternative, but it is a nifty collection of tools to work with dates.
https://github.com/hroptatyr/dateutils


### More information

Please, read tuptime-manual.txt for a complete reference guide.
