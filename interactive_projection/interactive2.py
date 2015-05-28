#!/usr/local/bin/python
import csv
import requests as rq
import sqlite3 as sq
from dateutil import parser
import datetime
import pytz
import json
#FRED Config
urls = {'GEOFRED':"http://geofred.stlouisfed.org/api/data"}
urls['GEO_REGION_TYPES'] =  urls['GEOFRED'] + "/regionTypes"
urls['GEO_MAPS'] =  "http://geofred-jason.stlouisfed.org/api/maps"
urls['GEO_DATA_TYPES'] =  urls['GEOFRED'] + "/groupAttributes"
urls['GEO_DATES'] =  urls['GEOFRED'] + "/groupDates"
urls['GEO_AGG'] =  urls['GEOFRED'] + "/aggregations"
urls['GEO_DATA'] =  urls['GEOFRED'] + "/group"
api_key = "fc359838e2193d76d75f8a850c41fbd7"

#change this DB location
db = "/Volumes/Pylos/Projects/FED/projection.db"
#

defFile = "chart_definitions.csv"
serFile = "iproj_series.csv"

conn = sq.connect(db) #connection is open
conn.row_factory = sq.Row
c = conn.cursor()
hashes = []
defs = []
cleanSeries = True;
cleanObs = False;
updateGeo = True;

def updateSeries():
	with open(serFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		if (cleanSeries):
			c.execute("DELETE from series")
		for row in reader:
			hash = row["series_hash"];
			print("series def ROW::")
			print(row)
			c.execute("select count(1) from series where series_hash = ? ", [row["series_hash"]])
			exists = c.fetchone()[0] == 1;
			print("row exists? "+str(exists))
			if not (exists) :
				print("inserting row")
				c.execute("INSERT INTO series (attributes, series_hash, series_name, region_type) VALUES (:attributes,:series_hash,:title,:region_type) ", row)
			
			dates = rq.get(urls["GEO_DATES"]+"/"+row["region_type"]+"/"+row["series_hash"]+"/"+row["attributes"]).json();
			print("DATES for series::")
			print(dates)
			#make a list of dates for all observations
			datelist = [elem["key"] for elem in dates]	
			print(datelist)
			c.execute("UPDATE series SET dates=? WHERE series_hash =?",(json.dumps(datelist), row["series_hash"]));
			conn.commit()
			
def getGeo():
	c.execute("DELETE from geo")
	for geo_type in ["county","state","country"]:
		jmap = rq.get(urls['GEO_MAPS']+"/"+geo_type).json()
		print(geo_type)
		print(jmap)
		c.execute("INSERT  INTO geo values(?,?)", (geo_type,json.dumps(jmap)))
		conn.commit()

def getObs():
	if (cleanObs):
		c.execute("DELETE from series")
	c.execute("SELECT * from series")
	for row in c.fetchall():
		print("updating series",row['series_name'])
		h = row["series_hash"];
		att = row["attributes"];
		region_type = row["region_type"]
		datelist =json.loads(row["dates"])
		ll = len(datelist);
		for date in datelist:
			
			c.execute("select count(1) from observations where series_hash = ? AND date=? ", (h,date))
			exists = c.fetchone()[0] == 1;
			
			if not (exists):
				print("datum not found, inserting")
				obs = rq.get(urls["GEO_DATA"]+"/"+region_type+"/"+h+"/"+att+"/"+date).json()
				#vals = obs['values']
				
				c.execute("INSERT INTO observations VALUES(?,?,?)", (h,date,json.dumps(obs)))
				conn.commit()
				print("commited %i to DB" % ll)
				ll = ll-1
			else:
				print("datum  %i already exists, skipping" % ll)
				ll = ll-1
			

		
'''			
def getDefs():
	with open(defFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		c = conn.cursor()
		c.execute("DELETE from series")
		for row in reader:
			defs.append(row)
			#use comprehensions to strip spaces and split hashes
			hsh = [x.strip() for x in row["series_hash"].split(',')]
			print("HASH")
			print(hsh)
			regionType = row["region_type"]
			# get "attributes" of row
			
			
			for h in hsh:
				attributes = rq.get(urls["GEO_DATA_TYPES"]+"/"+regionType+"/"+h).json()[0]['value']
				print(attributes)
				print(type(attributes))
				# get "dates" of row
				dates = rq.get(urls["GEO_DATES"]+"/"+regionType+"/"+h+"/"+attributes).json();
				#make a list of dates for all observations
				datelist = [elem["key"] for elem in dates]
				
				if seriesExists(h):
					print("updating series")
					c.execute("UPDATE geo SET dates=? WHERE series_hash =?",(datelist, h))
				else:
					name = rq.get(urls["GEO_DATA"]+"/"+regionType+"/"+h+"/"+attributes+"/"+datelist[0]).json()["title"];
					print("new series")
					print(name);
					c.execute("INSERT INTO series VALUES(?,?,?,?,?)", (attributes,hsh,name,regionType,json.dumps(datelist)))
				
				
					
					
					#get the map
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
'''		
	
def obsExists(hash, date):
	c.execute("select count(1) from observations where series_hash = ? AND date = ?",(hash, date))
	row = c.fetchone()
	return row[0] == 1

def seriesExists(hash):
	c.execute("select count(1) from observations where series_hash = ? ", [hash])
	row = c.fetchone()
	return row[0] == 1

def mapExists(region_type):
	c.execute("select count(1) from observations where region_type = ?",(region_type))
	row = c.fetchone()
	return row[0] == 1



updateSeries()
getObs()