var tracts_dict;
var converted_tracts = new Array();

function parseTractsJson(json){
	var coordinates, xCoord, yCoord, value;
	tracts_dict = JSON.parse(json);

	for(var key in tracts_dict) {
		value = tracts_dict[key];
		key = key.substring(1, key.length-1);
		coordinates = key.split(', ');
		xCoord = coordinates[0];
		yCoord = coordinates[1];
		
		var x = convert(xCoord);
		var y = convert(yCoord);

		var tmp = {x: x, y: y, firstDes: value[0], secondDes: value[1]};
		converted_tracts.push(tmp);
		
		
		renderTracts(x, y);
	}
}

function renderTracts(x, y){
var tmpX, tmpY, scaleX, scaleY, c;
		
	var tileX = x+tileSize;
	var tileY = y+tileSize;	
	console.log("tract at: " + tileX + " " + tileY);
	
	tract = game.add.sprite(tileX, tileY, 'tract');
	
	scaleX = (tileSize)/tract.width;	
	scaleY = (tileSize)/tract.height;
	tract.scale.setTo(scaleX,scaleY);
	
//	console.log("tract coordinates: " + x + " " + y);
	/*
	// logic for clustering lots
	tmpX = xCoord.toString().substring(2, xCoord.length);
	tmpY = yCoord.toString().substring(2, yCoord.length);

	if (tmpX.valueOf() == "25") {
		building.anchor.x = -0.1;
	} else if (tmpX.valueOf() == "75") {
		building.anchor.x = 0.3;
	}

	if (tmpY.valueOf() == "25") {
		building.anchor.y = -0.1;
	} else if (tmpY.valueOf() == "75") {
		building.anchor.y = 0.3;
	}
	
	// scale all the buildings smaller than roads
	scaleX = (gameSize/26)/building.width;	
	scaleY = (gameSize/26)/building.height;
	building.scale.setTo(scaleX,scaleY);
	
	// add this building to collection of buildings
	buildingGroup.add(building);
	
	//collisions
	addBuildingPhysics();*/
}