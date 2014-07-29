#!/usr/local/bin/python
import csv
import requests as rq
import sqlite3 as sq
from dateutil import parser
import datetime
import pytz
import json
#FRED Config
urls = {'GEOFRED':"http://geofred-jason.stlouisfed.org/api/data"}
urls['GEO_REGION_TYPES'] =  urls['GEOFRED'] + "/regionTypes"
urls['GEO_MAPS'] =  "http://geofred-jason.stlouisfed.org/api/maps"
urls['GEO_DATA_TYPES'] =  urls['GEOFRED'] + "/groupAttributes"
urls['GEO_DATES'] =  urls['GEOFRED'] + "/groupDates"
urls['GEO_AGG'] =  urls['GEOFRED'] + "/aggregations"
urls['GEO_DATA'] =  urls['GEOFRED'] + "/group"
api_key = "fc359838e2193d76d75f8a850c41fbd7"
db = "/Volumes/Pylos/Projects/FED/projection.db"
conn = sq.connect(db) #connection is open
conn.row_factory = sq.Row
c = conn.cursor()
hashes = []
defs = []

def openCSV():
	with open('chart_definitions.csv', 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		c = conn.cursor()
		c.execute("DELETE from series")
		for row in reader:
			defs.append(row)
			hsh = row["series_hash"]
			regionType = row["region_type"]
			print("hash : "+hsh)
			attributes = rq.get(urls["GEO_DATA_TYPES"]+"/"+regionType+"/"+hsh).json()[0]['value']
			print(attributes)
			dates = rq.get(urls["GEO_DATES"]+"/"+regionType+"/"+hsh+"/"+attributes).json();
			datelist = [elem["key"] for elem in dates]
			
			name = rq.get(urls["GEO_DATA"]+"/"+regionType+"/"+hsh+"/"+attributes+"/"+datelist[0]).json()["title"];
			print(name);
			jMap = rq.get(urls['GEO_MAPS']+"/"+regionType).json()
			print(urls['GEO_MAPS']+"/"+regionType)
			c.execute("SELECT * FROM geo WHERE region_type=?",[regionType])
			data = c.fetchone();
			print(data)
			if data is None: c.execute("INSERT INTO geo VALUES(?,?)", (regionType, json.dumps(jMap)))
			else: c.execute("UPDATE geo SET geometry=? WHERE region_type=?",(json.dumps(jMap),regionType)) 
			c.execute("INSERT INTO series VALUES(?,?,?,?)", (hsh,name,regionType,json.dumps(datelist)))
			conn.commit()
			print("commited series to DB")
				
			ll = len(datelist);
			for date in datelist:
				c.execute("SELECT * FROM observations WHERE date=? AND series_hash=?",[date,hsh])
				data = c.fetchone();
				if data is None:
					obs = rq.get(urls["GEO_DATA"]+"/"+regionType+"/"+hsh+"/"+attributes+"/"+date).json()
					#vals = obs['values']
					meta = obs['seriesMeta']
					c.execute("INSERT INTO observations VALUES(?,?,?)", (hsh,date,json.dumps(obs)))
					conn.commit()
					print("commited %i to DB" % ll)
					ll = ll-1
				else:
					print("data  %i already exists, skipping" % ll)
					ll = ll-1
	
def rowExists(hash, date):
	c.execute("select count(1) from observations where series_hash = ? AND date = ?",(hash, date))
	row = c.fetchone()
	return row[0] == 1

	

	
#print rowExists("f36ab932a8542c1386dcdf777f52c918","2013-04-01");
openCSV()