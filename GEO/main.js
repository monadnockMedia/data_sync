var map;
var data;
var cScale;
var val_keys;
val_arr = [];
	
	
	$(function(){
		queue()
			.defer(d3.json, "country.json")
			.defer(d3.json, "2011-01-01.json")
			.await(build)
		
	})	
	
	
var build = function(e, m , d){
	map = m;
	data = d;
	var w = 1024,h=768;
	
	val_keys = Object.keys(data.values);

	for (var i = 0; i<val_keys.length; i++){
		var val = data.values[val_keys[i]];
		val_arr.push(val);
		
	}
	
	var ex = d3.extent(val_arr, function(d){return +d});
	var step = Math.ceil(ex[1]-ex[0])/5;
	var dm = d3.range(ex[0], ex[1], step)
	
	cScale = d3.scale.linear().range(["blue","red","yellow","pink","red"])
		.domain(dm);
		
	
	var projection = d3.geo.mercator().scale(128).translate([w/2,h/2]);

	var pathG = d3.geo.path().projection(projection);

	var svg = d3.select("body").append("svg")
		.attr("width", w)
		.attr("height", h);
	
	
	var group = svg.append("g").attr("class","countries")
		
	group.selectAll("path").data(map.features).enter().append("path")
		.style({
			"fill": function(d){  
				var val = +data.values[+d.properties.gid];
				if(!isNaN(val)){
					return cScale(val) 
				}else{
					return("grey")
				}
			
				 
				}
		})
		.attr("d", pathG)
	
	group.selectAll("text").data(map.features).enter().append("text")
		.text(
			function(d){
				var l = +data.values[+d.properties.gid]
				return l.toFixed(0);
				})
		.attr({
			"transform": function(d) { 
				return "translate(" + projection(d.properties.centroid.coordinates) + ")" 
				}
		})
		
		
	
	
}