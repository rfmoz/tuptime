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

	System startups:	1   since   12:24:08 03/05/15
	System shutdowns:	0 ok   -   0 bad
	Average uptime: 	1 hours, 19 minutes and 38 seconds
	Current uptime: 	1 hours, 19 minutes and 38 seconds   since   12:24:08 03/05/15
	Uptime rate: 		100.0 %
	System time: 		1 hours, 19 minutes and 38 seconds

For keep it updated, add the init script or systemd file and a cron entry.

More information into Tuptime Manual "tuptime-manual.txt"
