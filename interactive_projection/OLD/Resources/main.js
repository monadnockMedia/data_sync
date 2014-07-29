//init function
var mapObject;
var mapString;
var ds;

var init = function(){
	console.log("init");
	ds = new datasource();
	ds.setup().then(function(){
		console.log(this);
		ds.getMap("county").then(function(d){
			mapObject = JSON.parse(d);
			mapString = JSON.stringify(mapObject);
			//$("#json").html(mapString);
		})
	});
	
}