function closestX(num, arr) {
	var curr = arr[0].x;
	var i;
	var indices = new Array();
	for (i = 0; i < arr.length; i++){
		if (Math.abs(num - arr[i].x) < Math.abs(num - curr)){
			curr = arr[i].x;
			
		}
	}
	for (i = 0; i < arr.length; i++){
		if (curr == arr[i].x) {
			indices.push(i);
		}
	}
//	console.log("closest x: " + curr);
	
	return indices;
}

function closestY(num, arr, indices) {
	var i;
	var j=indices[0];//the first index element
	var curr = arr[j].y;//curr is the value of y at first index
	var finalIndex;
	
	for (i = 1; i < indices.length; i++){//for each element(index) in indices array
		j = indices[i];
		if (Math.abs(num - arr[j].y) <= Math.abs(num - curr)){
			curr = arr[j].y;
			
		}
	}
	for (i = 0; i < indices.length; i++){//for each index in indices array
		j = indices[i];
		if (curr == arr[j].y) {//if the closest element we found is the element at that index
			finalIndex = j;
			
			//always returning the last of the indices..
			console.log("closest y: " + curr);
			return finalIndex;
		}
	}
	
}

function checkHitBuilding(){
	if (game.physics.arcade.collide
			(player, buildingGroup)){
//TODO: inner corners of tracts buggy
			var pX = Math.floor(player.x);
			var pY = Math.floor(player.y);
			var indices = closestX(pX, converted_lots); // return indices
			var index = closestY(pY, converted_lots, indices);
			if (converted_lots[index].firstDes == "None") {
				console.log(converted_lots[index].secondDes);
			} else {
				console.log(converted_lots[index].firstDes);
			}

	}
}


