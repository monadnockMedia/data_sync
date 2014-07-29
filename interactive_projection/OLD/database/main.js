var defs;
var data;
var init = function(){
	console.log("init");

	ds = new datasource();	//create an instance of the datasource
	ds.setup().then(		//call setup() and wait for the deffered
		function(d){
			defs = d;		//to get the definitions, which is an object whose keys are categories
			getData();		//go get some data
		}
		
		);
}

var getData = function(){
	ds.getByName("Unemployment Rate").then(function(d){
		data = d;
		$("#json").text(JSON.stringify(Object.keys(d),null,2))	
	})
}