#!/usr/local/bin/python
import requests as rq
import sqlite3 as sq
from dateutil import parser
import datetime
import pytz
import json
#FRED Config
urls = {'FRED':"http://api.stlouisfed.org/fred"}
urls['FRED_SER'] =  urls['FRED'] + "/series"
urls['FRED_OBS'] =  urls['FRED_SER'] + "/observations"
api_key = "fc359838e2193d76d75f8a850c41fbd7"
args = {"api_key":api_key, "series_id":0, "file_type":"json", "frequency":"sa", "aggregation_method" : "avg"}  #initial arguments for FRED requests


#DB config
db = 'unemployment.db'
conn = sq.connect(db) #connection is open
conn.row_factory = sq.Row
force = False;
#setup vars
today = datetime.datetime.now()
today = pytz.utc.localize(today);
stamp = today.strftime("%Y-%m-%d %H:%M:%S%z")

#get string date for one decade ago
tmpStamp = today.strftime("%Y-%m-%d")
lDate = tmpStamp.split("-")
lDate[0] = str(int(lDate[0]) - 10);
startDate = datetime.date(int(lDate[0]),int(lDate[1]),int(lDate[2]))
startStr = lDate[0]+"-"+lDate[1]+"-"+lDate[2]
args["observation_start"] = startStr

def get_ids():
	c = conn.cursor()
	c.execute("SELECT series_id FROM ser_id");
	rows = c.fetchall()
	return rows

#check that all series are present, and up to date.
def check_series():
	if force == True:
		delete_rows()
	ids = get_ids() #get all ids from db
	#print ids
	c = conn.cursor()
	for id in ids:
		i = (id["series_id"],)
		if i[0] != "N/A":
			c.execute("SELECT * FROM ser_data WHERE ser_id=?",i)
			data = c.fetchone();
			if data is None or force == True: #this id is not in db
				print('There is no series named %s in database, syncing with FRED...'%i)
				create_series(i)
			else: #id is found
				date_check = check_date(data["date"]) #check if up to date
				if date_check: 
					update_series(i)



def get_series(id):
	args["series_id"] = id;
	r = rq.get(urls["FRED_SER"], params=args)
	j = r.json();
	_date = j["seriess"][0]["last_updated"]
	return {"series":j, 'date':_date}

def get_obs(id):
	args["series_id"] = id;
	r = rq.get(urls["FRED_OBS"], params=args)
	j = r.json();
	_obs = j["observations"]
	nullItems = []
	for (oi, ob) in enumerate(_obs):
		if ob["value"] == ".":
			nullItems.append(oi)
			print("Null Items found at "+str(oi))
			_obs[oi] = "null"
	for (ni, nn) in enumerate(nullItems):
		_obs.remove("null")
#	print _obs
	return _obs
	
def create_series(id):
	c = conn.cursor()
	obs = get_obs(id)
	ser = get_series(id)
	date = ser["date"]
	ser = ser["series"]
	q = (id,ser,obs,date);
	c.execute("INSERT INTO ser_data VALUES(?,?,?,?,?)", (stamp,str(id[0]),json.dumps(ser),json.dumps(obs),date))
	conn.commit()

def delete_rows():
	c = conn.cursor()
	c.execute("DELETE FROM ser_data")
	conn.commit()
	
def check_date(d):
	data_date = parser.parse(d);
	data_utc = data_date.astimezone(pytz.utc);
	check = today < data_utc
	return check

def update_series(id):
	c = conn.cursor()
	obs = get_obs(id)
	ser = get_series(id)
	date = ser["date"]
	ser = ser["series"]
	q = (id,ser,obs,date);
	c.execute("UPDATE ser_data SET series = ?, observations = ?, date = ?, updated = ? WHERE ser_id = ? ", (json.dumps(ser),json.dumps(obs),date,stamp, str(id[0])))
	conn.commit();
	print("seriess updated")
	
check_series()
