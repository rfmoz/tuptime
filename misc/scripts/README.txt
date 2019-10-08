#### Scripts #####




____Tools____

tuptime_dbcheck.py
    Test database integrity. Catch and fix errors.

tuptime_join.py
    Join two tuptime db files into an other one.




____DB migrations____

db-tuptime-migrate.sh
    Update tuptime database format from versions previous than 3.0.00.


db-tuptime-migrate-3.0-to-3.1.sh
    Update tuptime database format from version 3.0.00 to 3.1.00.


db-tuptime-migrate-3.1-to-4.0.sh
    Update tuptime database format from version 3.1.0 or above to to 4.0.0.
    Tuptime v.4 do it automatically.


uptimed-to-tuptime.py
    Migrate Uptimed records to Tuptime.




____Plots____

tuptime-barchart_from_db.py
    Graph a daily plot reading directly from tuptime database.


tuptime-barchart_from_csv.py
    Graph a daily plot from tuptime csv output.
