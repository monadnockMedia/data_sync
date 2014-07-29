#!/usr/local/bin/python
import csv
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
args = {"api_key":api_key, "series_id":0, "units":"pc1","file_type":"json", "frequency":"m"}  #initial arguments for FRED requests
ids = []
read = []
natID = "CPIAUCSL";


def openCSV():
	with open('inflation.csv', 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			ids.append(row["ser_id"])
			read.append(row)
		i = 0
		for id in ids:
			o = get_obs(id)
			val = o[len(o)-1]["value"]
			print val
			print i
			read[i]["value"] = val;
			i+=1
		nat = get_obs(natID)
		print nat[len(nat)-1]
		rate = nat[len(nat)-1]["value"]
		jsRead = json.dumps(read)
		jsFile = "var data_json = JSON.parse('"+jsRead+"');"
		jsFile += "var national_rate ="+rate+";"
		with open("data.js","w") as outfile:
			outfile.write(jsFile)
		

def get_obs(id):
	args["series_id"] = id;
	r = rq.get(urls["FRED_OBS"], params=args)
	j = r.json();
	_obs = j["observations"]
	nullItems = []
	for (oi, ob) in enumerate(_obs):
		if ob["value"] == ".":
			nullItems.append(oi)
			_obs[oi] = "null"
	for (ni, nn) in enumerate(nullItems):
		_obs.remove("null")
#	print _obs
	return _obs

openCSV()