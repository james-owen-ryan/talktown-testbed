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
		
 
	for (var i = 0; i < 2; i++){
		for (var j = 0; j < 2; j++) {
			var tileX = x+(i*tileSize);
			var tileY = y+(j*tileSize);
			if (value == "House") {
				if (i == 0 && j == 0) { building = game.add.sprite(tileX, tileY, 'houseUL'); }
				else if (i == 0 && j == 1) { building = game.add.sprite(tileX, tileY, 'houseLL'); }
				else if (i == 1 && j == 0) { building = game.add.sprite(tileX, tileY, 'houseUR'); }
				else if (i == 1 && j == 1) { building = game.add.sprite(tileX, tileY, 'houseLR'); }
				
			} else if (value == "NoneType") {
				if (i == 0 && j == 0) { building = game.add.sprite(tileX, tileY, 'empty_lot'); }
				else if (i == 0 && j == 1) { building = game.add.sprite(tileX, tileY, 'empty_lot'); }
				else if (i == 1 && j == 0) { building = game.add.sprite(tileX, tileY, 'empty_lot'); }
				else if (i == 1 && j == 1) { building = game.add.sprite(tileX, tileY, 'empty_lot'); }
			
			} else {
				if (i == 0 && j == 0) { building = game.add.sprite(tileX, tileY, 'business'); }
				else if (i == 0 && j == 1) { building = game.add.sprite(tileX, tileY, 'business'); }
				else if (i == 1 && j == 0) { building = game.add.sprite(tileX, tileY, 'business'); }
				else if (i == 1 && j == 1) { building = game.add.sprite(tileX, tileY, 'business'); }
			}
			helper(building, xCoord, yCoord);
		}
	}
	


}

function helper(building, xCoord, yCoord) {
	var tmpX, tmpY, scaleX, scaleY, c;
	// logic for clustering lots
	var tmpX = xCoord.toString().substring(2, xCoord.length);
	var tmpY = yCoord.toString().substring(2, yCoord.length);

	if (tmpX.valueOf() == "25") {
		building.anchor.x = 0.35;
	} else if (tmpX.valueOf() == "75") {
		building.anchor.x = 0.65;
	}

	if (tmpY.valueOf() == "25") {
		building.anchor.y = 0.35;
	} else if (tmpY.valueOf() == "75") {
		building.anchor.y = 0.65;
	}
	
	scaleX = (tileSize)/building.width;	
	scaleY = (tileSize)/building.height;
	building.scale.setTo(scaleX,scaleY);
	
	// add this building to collection of buildings
	buildingGroup.add(building);
	
	//collisions
	addBuildingPhysics(building);
	
}
