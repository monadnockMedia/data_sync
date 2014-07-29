
var Datasource = function(){
	defs = "../chart_definitions.csv"
	this.def;
	self = this;
	this.session;
	
	var connection = {};
	startSession = function(){
		console.log("attempt connection", autobahn);
		connection = new autobahn.Connection({
			url: 'ws://localhost:8080/ws',
			realm: 'iproj'
		});
		connection.onopen = function(session) {
				self.session = session; 
				console.log("connection open", session);
				session.call("iproj.rpc.config", self.def, {}).then(function(r){console.log(r)});
		}
		connection.open();
	}

	console.log(connection);
	
	this.setup = function(){
		var dfd = $.Deferred();
		d3.csv(defs,function(d){
			console.log(d);
			
			
			$def = $(d);
			
			var res = {};
			$def.each(function(i,d){
				d.series_hash = d.series_hash.split(',').map(function(a){return a.replace(/\s+/g, '')});
				console.log(d)
				console.log(d.category);
				if(!res.hasOwnProperty(d.category)){
					res[d.category] = [];
				}
				
				res[d.category].push(d);
			})
			$def.promise().done(function(){
				console.log("done loading csv")
			})
			self.def = d;
			startSession();
			dfd.resolve(res);
			
		});
		return dfd.promise();
	}
	

	
	this.get = function(_id){
		var dfd = $.Deferred();
		 
		var o = this.def.map(function(d){  if (+d.id ==  _id){return d}});
		console.log("o:");
		console.log(o);
		var q = queue();
			q.defer(d3.json, o[0].region_type+".json")
			q.defer(d3.json, o[0].series_hash+".json")
			
		q.awaitAll(function(e,r){
			if(e){dfd.reject(e)}else{
			dfd.resolve( {map:r[0], data: [r[1]]}  )}
			
		})
		return dfd.promise();
	}
	
	this.getByName = function(_name){
		var id;
		$.each(this.def, function(i,d){
			if(d["chart_name"] == _name){
				id = d.id;
				console.log("id: ");
				console.log(d.id);
				return;
			} 
		})
		return self.get(id);
	}
	
	
}


