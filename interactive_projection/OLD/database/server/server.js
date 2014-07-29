// Make code portable to Node.js without any changes
var sqlite3 = require('sqlite3').verbose();
var db;

db = new sqlite3.Database("./projection.db", sqlite3.OPEN_READONLY);



try {
	var autobahn = require('autobahn');
} catch (e) {
	// when running in browser, AutobahnJS will
	// be included without a module system
}
var def;
var sess;
// Set up WAMP connection to router
var connection = new autobahn.Connection({
	url: 'ws://localhost:8080/ws',
	realm: 'iproj'
});

// Set up 'onopen' handler
connection.onopen = function(session) {
	sess = session;
	Object.keys(methods).forEach(function(k){
		console.log("registering ",'iproj.rpc.'+k, "function");
		sess.register('iproj.rpc.'+k, methods[k]).then(
			function(registration) {
				// registration succeeded, registration is an instance of autobahn.Registration
				console.log("succeeded:: ",registration.id);
			}, function(error) {
				// registration failed, error is an isntance of autobahn.Error
				console.log(error);
			});;
	})
	

};

var methods = {};
methods.ping = function(){
	console.log("ping");
	return "pong";
}

methods.getGeo = function(_a, _o){
	var df = connection.defer();
	console.log(df);
	var reg = def;
	db.all("SELECT * from geo WHERE region_type = ?", [_o.region], function(e,r){df.resolve(JSON.parse(r))});
	return df.promise;
}
var thedeets;

methods.getObs = function(_a, _o, _deets){
	var data = [];
	console.log("getting observations", _o.series_hash, _deets)
	var i = 0;
	var deets = _deets;
	thedeets = _deets;
	var df = connection.defer();
	db.each("SELECT metadata from observations WHERE series_hash = ?", [_o.series_hash], 
		function(e,r){
			console.log(i);
			rj = JSON.parse(r.metadata);
			data.push(rj)
			//_deets.progress([r],rj);
			_deets.progress([i]);
			i++;
			},
		function(e,r){
			console.log(r+"rows transmitted");
			df.resolve(data);
		}
	
	);
	return df.promise;
}

methods.config = function(_a, _o){
	def = _a;
	return("config received");
}



connection.open();


			
