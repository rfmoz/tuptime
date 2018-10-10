tuptime
=======

Tuptime is a tool for report the historical and statistical running time of the system, keeping it between restarts. Like uptime command but with more interesting output.


### Basic Installation and usage

#### Package installation

* Debian: https://packages.debian.org/tuptime
* Ubuntu: https://packages.ubuntu.com/tuptime
* ArchLinux: https://aur.archlinux.org/packages/tuptime
* FreeBSD: https://www.freshports.org/sysutils/tuptime

#### Manual installation

In a Linux or FreeBSD system...

Clone the repo:

	git clone https://github.com/rfrail3/tuptime.git

Copy the "tuptime" file located under "latest/" directory to "/usr/bin/" and make it executable:

	cp tuptime/src/tuptime /usr/bin/tuptime
	chmod ugo+x /usr/bin/tuptime

Assure that the system pass the prerequisites:

	python 3.X 

Run first with a privileged user:

	tuptime

#### Examples

Sample output after install:

	System startups:	1   since   21:54:09 24/09/15
	System shutdowns:	0 ok   -   0 bad
	System uptime: 		100.0 %   -   21 minutes and 30 seconds
	System downtime: 	0.0 %   -   0 seconds
	System life: 		21 minutes and 30 seconds

	Largest uptime:		21 minutes and 30 seconds   from   21:54:09 24/09/15
	Shortest uptime:	21 minutes and 30 seconds   from   21:54:09 24/09/15
	Average uptime: 	21 minutes and 30 seconds

	Largest downtime:	0 seconds
	Shortest downtime:	0 seconds
	Average downtime: 	0 seconds

	Current uptime: 	21 minutes and 30 seconds   since   21:54:09 24/09/15

If you do the same a few days after, the output may will be more similar to this:

	System startups:	110   since   10:15:27 08/08/15
	System shutdowns:	107 ok  <-   2 bad
	System uptime: 		4.04 %   -   1 days, 22 hours, 4 minutes and 44 seconds
	System downtime: 	95.96 %   -   45 days, 13 hours, 57 minutes and 30 seconds
	System life: 		47 days, 12 hours, 2 minutes and 15 seconds

	Largest uptime:		2 hours, 10 minutes and 44 seconds   from   20:49:17 09/08/15
	Shortest uptime:	9 seconds   from   10:23:36 08/08/15
	Average uptime: 	25 minutes and 8 seconds

	Largest downtime:	7 days, 10 hours, 17 minutes and 26 seconds   from   06:09:45 10/08/15
	Shortest downtime:	15 seconds   from   19:27:24 19/09/15
	Average downtime: 	9 hours, 56 minutes and 42 seconds

	Current uptime: 	23 minutes and 33 seconds   since   21:54:09 24/09/15

Or this, with -t | --table option:

	No.      Startup Date                              Uptime       Shutdown Date   End                   Downtime
                                                                                                                                    
	1   10:15:27 08/08/15                          42 seconds   10:16:09 08/08/15    OK                 16 seconds
	2   10:16:26 08/08/15                          49 seconds   10:17:15 08/08/15    OK                 16 seconds
	3   10:17:32 08/08/15            5 minutes and 47 seconds   10:23:19 08/08/15    OK                 16 seconds
	4   10:23:36 08/08/15                           9 seconds   10:23:45 08/08/15   BAD                 42 seconds
	5   10:24:28 08/08/15   2 hours, 9 minutes and 27 seconds   12:33:55 08/08/15    OK  41 minutes and 44 seconds
        . . .

Or this, with -l | --list option:

	Startup:  1  at  10:15:27 08/08/15
	Uptime:   42 seconds
	Shutdown: OK  at  10:16:09 08/08/15
	Downtime: 16 seconds

	Startup:  2  at  10:16:26 08/08/15
	Uptime:   49 seconds
	Shutdown: OK  at  10:17:15 08/08/15
	Downtime: 16 seconds

	Startup:  3  at  10:17:32 08/08/15
	Uptime:   5 minutes and 47 seconds
	Shutdown: OK  at  10:23:19 08/08/15
	Downtime: 16 seconds
	. . .

Don't forget! For keep it updated, add it to the init system, to the cron service and use 'tuptime' user for execution. (All scripts, units and related files are provided inside this repo)



### What offer tuptime different than other alternatives like uptimed and downtimed

- It doesn't run as a daemon, at least, it only need execution when the init manager startup and shutdown the system. For avoid problems with behaviours that can produce a switch off without a proper shutdown, like power failures, a cron job and a .timer unit are shipped with the project for update the registers each n minutes. As a system administrator, you can easily choose the best number for your particular system requirements.

- It is written in Python using common modules and as few as possible, easy to see what is inside it, and modify it for fit for your particular use case.

- It registers the times in a sqlite database. Any other software can use it. The specs are in the tuptime-manual.txt. Also, it has the option to output the registers in seconds and epoch (-s) or/and in csv format, easy to pipe it to other commands.

- Its main purpose is tracking all the system startups/shutdowns and present that information to the user in a more understandable way. Don't have mail alerts when a milestones are reached or the limitation of keep the last n records.

- Its written for avoid false startups registers, actually there are some issues with other alternatives related to that. This is an issue that sometimes happens on virtualized enviroments, servers with high load or when ntp are running.

- It can report the whole life of the system or only a part of that life, closing the range between startups/shutdowns or timestamps.


### More information

Please, read tuptime-manual.txt for a complete reference guide.
