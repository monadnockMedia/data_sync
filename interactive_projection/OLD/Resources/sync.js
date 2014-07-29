var when = require("when");
var fs = require("fs");

var datasync = function(){
	this.setup = function(){
		var dfd = when.defer();
		sqlite3 = require('sqlite3').verbose();
		this.db = new sqlite3.Database(
			"/Volumes/Pylos/Projects/FED/data_sync/projection.db", sqlite3.OPEN_READONLY, function(e){dfd.resolve(e)})
			return dfd.promise;
	}
	
	this.syncObservations = function( _hash ){
		var res = [];
		var dfd = when.defer();
		this.db.each("SELECT * FROM observations WHERE series_hash = ?", _hash, function(e,d){
			
			res.push(JSON.parse(d["metadata"]));
		}, function(){
			
			fs.writeFile( _hash+".json", JSON.stringify(res), function(){
				dfd.resolve(_hash+".json");
			})
		})
		
		return dfd.promise;
	}
	
	this.syncMap = function( _regionType ){
		var dfd = when.defer();
		this.db.get("SELECT * FROM geo WHERE region_type = ?", _regionType, function(e,d){
			fs.writeFile( _regionType +".json", d.geometry, function(){
				dfd.resolve(_regionType+".json");
			})
		})

		return dfd.promise;
	}
	
	this.setup().then(this.syncMap("county"));
}


