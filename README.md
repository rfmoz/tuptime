tuptime
=======

Tuptime is a tool for report the historical and statistical running time of the system, keeping it between restarts. Like uptime command but with more interesting output.


### Basic Installation and usage

Clone the repo:
	git clone https://github.com/rfrail3/tuptime.git

Copy the "tuptime" file located under "latest/" directory to "/usr/bin/" and make it executable:

	cp tuptime/latest/tuptime /usr/bin/tuptime
	chmod ugo+x /usr/bin/tuptime

Assure that the system pass the prerequisites:

	Linux or FreeBSD with python 2.7 or 3.X 

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

If you do the same a few days after, the output may will be more similar to this:

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

Don forguet! For keep it updated, add the init script or systemd file and a cron entry.



### More information

Please, read tuptime-manual.txt for a complete reference guide.
