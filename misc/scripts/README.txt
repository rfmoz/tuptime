#### Scripts #####


____Tools____

tuptime_dbcheck.py
    Test database integrity. Catch and fix errors.

tuptime_join.py
    Join two tuptime db files into an other one.

tuptime_modify.py
    Modify registers keeping nearest values in sycn.
    Allow change 'end status', 'startup date' and 'shutdown date'.



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

tuptime-barchart_from_db.py
    Graph a daily plot reading directly from tuptime database.


tuptime-barchart_from_csv.py
    Graph a daily plot from tuptime csv output.
