# Data Sync scripts for St. Louis Fed project.
***

#unemployment/unemployment.py
+ loops through unemployment.db, checking dates and series IDs, pulls updated JSON from FRED as necessary.
+ usage:

	`$python unemployment.py`

* Note: change value of force (line 20) to force update.
* Python module dependencies:
    + requests
    + sqlite3
    + dateutil
    + datetime
    + pytz
    + json

#inflation/inflation.py
+ generates flat file data.js based on IDs in inflation.csv
+ usage:

    `$python inflation.py`

