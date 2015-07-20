tuptime
=======

Tuptime is a tool for report the historical and statistical running time of the system, keeping it between restarts. Like uptime command but with more interesting output.


### Basic Installation and usage

Clone the repo:
	git clone https://github.com/rfrail3/tuptime.git

Copy the "tuptime" file located under "latest/" directory to "/usr/bin/" and make it executable:

	cp tuptime/latest/tuptime /usr/bin/tuptime
	chmod ugo+x /usr/bin/tuptime

Run first with a privileged user:

	tuptime

And you will get some similar to this:

	System startups:	1   since   12:50:34 07/16/15
	System shutdowns:	0 ok   -   0 bad
	Average uptime: 	2 hours, 2 minutes and 41 seconds
	Average downtime: 	0 seconds
	Current uptime: 	2 hours, 2 minutes and 41 seconds   since   12:50:34 07/16/15
	Uptime rate: 		100.0 %
	Downtime rate: 		0.0 %
	System uptime: 		2 hours, 2 minutes and 41 seconds
	System downtime: 	0 seconds
	System life: 		2 hours, 2 minutes and 41 seconds

If you do the same a few days ago, the output may will be more similar to this:

	System startups:	60   since   16:31:28 05/06/15
	System shutdowns:	59 ok   -   0 bad
	Average uptime: 	7 hours, 6 minutes and 36 seconds
	Average downtime: 	21 hours, 15 minutes and 45 seconds
	Current uptime: 	6 hours, 44 minutes and 48 seconds   since   08:08:53 07/16/15
	Uptime rate: 		25.05993 %
	Downtime rate: 		74.94007 %
	System uptime: 		17 days, 18 hours, 36 minutes and 46 seconds
	System downtime: 	53 days, 3 hours, 45 minutes and 27 seconds
	System life: 		70 days, 22 hours, 22 minutes and 13 seconds

And if you add the enumerate (-e) option, the system life will be printed:

	Startup:  1  at  10:03:31 05/03/15
	Uptime:   2 minutes and 9 seconds
	Shutdown: OK  at  10:05:40 05/03/15

	Downtime: 15 seconds

	Startup:  2  at  10:05:56 05/03/15
	Uptime:   3 minutes and 14 seconds
	Shutdown: OK  at  10:09:10 05/03/15

	Downtime: 1 hours, 40 minutes and 56 seconds

	Startup:  3  at  11:50:07 05/03/15
	Uptime:   9 seconds
	Shutdown: BAD  at  11:50:16 05/03/15


Don forguet! For keep it updated, add the init script or systemd file and a cron entry.



### More information

Please, read tuptime-manual.txt for a complete reference guide.
