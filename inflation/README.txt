This Readme is for the data-sync scripts for the inflation calculators: inflation.py

Running this script will produce a file named 'data.js' in the working directory.  The output file contains the JSON-formatted data used in the javascript application.

To run this script, first insure that required python modules are installed:
	csv, requests, sqlite3, dateutil, datetime, pytz, json
	
Run the script with python:
	$python inflation.py