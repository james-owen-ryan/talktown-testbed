var blocks_list;
/********************************************
*                                           *
*       parse and render block              *
*                                           *
********************************************/
function parseBlocksJson(json){
	var coordinates, startX, startY, endX, endY, dir, length;
	blocks_list = JSON.parse(json);
	length = blocks_list.length;
	// parse coordinates given by sim
	for (var i = 0; i < length; i++) {
		coordinates = blocks_list[i].split(', ');

		startX = coordinates[0];
		startX = startX.substring(3, startX.length);

		startY = coordinates[1];
		startY = startY.substring(0, startY.length-2);

		endX = coordinates[2];
		endX = endX.substring(2, endX.length);

		endY = coordinates[3];
		endY = endY.substring(0, endY.length-3);

		if (startX == endX) { dir = "v"; }
		else if (startY == endY) { dir = "h"; }
		renderBlocks(startX, startY, endX, endY, dir);
	}

}

function renderBlocks(startX, startY, endX, endY, dir){
	var x, y, cont, block, scaleX, scaleY;

	x = convert(startX);
	y = convert(startY);


	ex = convert(endX);
	ey = convert(endY);


	
	cont = true;
	while (cont){
	
		if (dir == "v") {
			block = game.add.sprite(x, y, 'verBlock');
			y += 1;
			if (y > ey) {
				cont = false;
			}
		} else if (dir == "h") {
			block = game.add.sprite(x, y, 'horBlock');
			x += 1;
			if (x > ex) {
				cont = false;
			}
		}

		scaleX = tileSize/block.width;	
		scaleY = tileSize/block.height;
		block.scale.setTo(scaleX,scaleY);
		
		streetGroup.add(block);

	}	
}
