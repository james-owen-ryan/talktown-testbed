var lots_dict;
var converted_lots = new Array();
/********************************************
*                                           *
*       parse and render lots               *
*                                           *
********************************************/


function parseLotsJson(json){
	
	var coordinates, xCoord, yCoord, value, type;
	lots_dict = JSON.parse(json);
	// parse coordinates given by sim
	for(var key in lots_dict) {
		value = lots_dict[key]; // value is treated as an array ?? perhaps json dicts keep intact
		type = value[0];
		key = key.substring(1, key.length-1);
		coordinates = key.split(', ');
		xCoord = coordinates[0];
		yCoord = coordinates[1];
		
		var x = convert(xCoord);
		var y = convert(yCoord);

		var tmp = {x: x, y: y, firstDes: value[1], secondDes: value[2]};
		converted_lots.push(tmp);
		
		
		
		renderLots(xCoord, yCoord, x, y, type);
	}
}


function renderLots(xCoord, yCoord, x, y, value){
	var tmpX, tmpY, scaleX, scaleY, c;
		
 
	for (var i = 0; i < 2; i++){
		for (var j = 0; j < 2; j++) {
			
			if (value == "House") {
				building = game.add.sprite(x+(i*tileSize), y+(j*tileSize), 'house');
			} else if (value == "NoneType") {
				building = game.add.sprite(x+(i*tileSize), y+(j*tileSize), 'empty_lot');
			} else {
				building = game.add.sprite(x+(i*tileSize), y+(j*tileSize), 'business');
			}
			helper(building);
		}
	}
	
/*	// logic for clustering lots
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
	}*/
	
/*	// scale all the buildings smaller than roads
	scaleX = (gameSize/49)/building.width;	
	scaleY = (gameSize/49)/building.height;
	building.scale.setTo(scaleX,scaleY);
	
	// add this building to collection of buildings
	buildingGroup.add(building);
	
	//collisions
	addBuildingPhysics(building);
	*/

	
	
}

function helper(building) {
	scaleX = (tileSize)/building.width;	
	scaleY = (tileSize)/building.height;
	building.scale.setTo(scaleX,scaleY);
	
	// add this building to collection of buildings
	buildingGroup.add(building);
	
	//collisions
	addBuildingPhysics(building);
	
}
