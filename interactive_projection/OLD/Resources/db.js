var when = require("when")
var datasource = function(){
	
	
	this.setup = function(){
		var dfd = when.defer();
		sqlite3 = require('sqlite3').verbose();
		this.db = new sqlite3.Database(
			"/Volumes/Pylos/Projects/FED/data_sync/projection.db", sqlite3.OPEN_READONLY, function(e){dfd.resolve(e)})
			return dfd.promise;
	}
	
	this.getObservations = function( _hash ){
		var res = [];
		var dfd = when.defer();
		this.db.each("SELECT * FROM observations WHERE series_hash = ?", _hash, function(e,d){
			res.push(d);
		}, function(){
			dfd.resolve(res);
		})

		return dfd.promise;
	}
	
	this.getMap = function( _regionType ){
		var dfd = when.defer();
		this.db.get("SELECT * FROM geo WHERE region_type = ?", _regionType, function(e,d){
			dfd.resolve(d.geometry);
		})

		return dfd.promise;
	}
	
}


