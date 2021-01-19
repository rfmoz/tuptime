#### Scripts #####


____Tools____

tuptime_dbcheck.py
    Test database integrity. Catch and fix errors.

tuptime_join.py
    Join two tuptime db files into an other one.

tuptime_modify.py
    Modify registers keeping nearest values in sync.
    Allow change 'end status', 'startup timestamp' and 'shutdown timestamp'.



____DB migrations____

db-tuptime-migrate-2.0-to-3.0.sh
    Update tuptime database format from version 2.0.0 or above to 3.0.0.


db-tuptime-migrate-3.0-to-3.1.sh
    Update tuptime database format from version 3.0.0 to 3.1.0.


db-tuptime-migrate-3.1-to-4.0.sh
    Update tuptime database format from version 3.1.0 or above to 4.0.0.
    Tuptime v.4 do it automatically.


db-tuptime-migrate-4.0-to-5.0.sh
    Update tuptime database format from version 4.0.0 or above to 5.0.0.
    Tuptime v.5 do it automatically.



____Plots____

tuptime-plot1.py
    Graph a plot with the number of hours (default) or events (-x swich)
    per state along each day. It gets the info from tuptime csv output.
    Playground script.

tuptime-plot2.py
    Graph a plot with the state events per hour along each day (default)
    or accumulated events per hour (-x swich). It gets the info from
    tuptime csv output. Playground script.
