//TODO: fix window arith

/********************************************
*                                           *
*       parse and render lots               *
*                                           *
********************************************/
var preloadReady = false;

function parseLotsJson(json){
	var coordinates;
	var xCoord;
	var yCoord;
	var dict = JSON.parse(json);
	for(var key in dict) {
		var value = dict[key];
		console.log(key, value);
		key = key.substring(1, key.length-1);
		coordinates = key.split(', ');
		xCoord = coordinates[0];
		yCoord = coordinates[1];
		renderLots(xCoord, yCoord, value);
	}
}

function renderLots(x, y, value){
	var width = ((x-0.625)*(window.innerWidth/8))-(window.innerWidth/8/2);
	var height = ((y-0.625)*(window.innerHeight/8))-(window.innerHeight/8/2);
	var posX = x.toString().substring(2, x.length);
	var posY = y.toString().substring(2, y.length);
	if (value == "House") { 
		var sprite = game.add.sprite(width,
									 height,
									 'house');
	} else if (value == "NoneType") {
		var sprite = game.add.sprite(width,
									 height,
									 'empty_lot');
	} else {
		var sprite = game.add.sprite(width,
 									 height,
									 'business');
	}
	//var scaleX = (window.innerWidth/33)/sprite.width;	
	//var scaleY = (window.innerHeight/33)/sprite.height;

///*
	var scaleX = (window.innerWidth/23)/sprite.width;	
	var scaleY = (window.innerHeight/23)/sprite.height;
	//depending on x and y, assign pivot and scale larger
	//set x anchor

	if (posX.valueOf() == "25") {
		sprite.anchor.x = 0.0;
	} else if (posX.valueOf() == "75") {
		sprite.anchor.x = 0.3;
	}
	//set y anchor
	if (posY.valueOf() == "25") {
		sprite.anchor.y = 0.0;
	} else if (posY.valueOf() == "75") {
		sprite.anchor.y = 0.3;
	}
	/**/
	sprite.scale.setTo(scaleX,scaleY);

}


/********************************************
*                                           *
*       parse and render block              *
*                                           *
********************************************/


function parseBlocksJson(json){
	var coordinates;
	var startX;
	var startY;
	var endX;
	var endY;
	var dir;
	var dict = JSON.parse(json);
	for(var start in dict) {
		var end = dict[start];
		console.log("start is" + start + " end is " + end);
		start = start.substring(1, start.length-1);
		coordinates = start.split(', ');
		startX = coordinates[0];
		startY = coordinates[1];
		end = end.substring(1, end.length-1);
		coordinates = end.split(', ');
		endX = coordinates[0];
		endY = coordinates[1];
		if (startX == endX) { dir = "v"; }
		else if (startY == endY) { dir = "h"; }
		renderBlocks(startX, startY, endX, endY, dir);
	}

}

function renderBlocks(startX, startY, endX, endY, dir){
	var x = ((startX-0.625)*(window.innerWidth/8))-(window.innerWidth/8/2);
	var y = ((startY-0.625)*(window.innerHeight/8))-(window.innerHeight/8/2);
	var cont;
	console.log("dir is "+dir);	
	cont = true;
	while (cont){
		var sprite = game.add.sprite(x, y, 'block');
		var scaleX = (window.innerWidth/33)/sprite.width;	
		var scaleY = (window.innerHeight/33)/sprite.height;
		sprite.scale.setTo(scaleX,scaleY);
	
		if (dir == "v") {
			y += 1;
			if (y > ((endY-scaleX)*(window.innerHeight/8))-(window.innerHeight/8/2)) {
				cont = false;
			}
		} else if (dir == "h") {
			x += 1;
			if (x > ((endX-scaleY)*(window.innerHeight/8))-(window.innerHeight/8/2)) {
				cont = false;
			}
		}
	}

}



/********************************************
*                                           *
*       load house, empty ,and business     *
*       lots sprites                        *
*                                           *
********************************************/

function preload() {
	
	game.load.image('house', 'Sprites/house.png');
	game.load.image('empty_lot', 'Sprites/empty_lot.png');
	game.load.image('business', 'Sprites/business.png');
	game.load.image('block', 'Sprites/block.png');


	preloadReady = true;

}
function create() {
}

function update() {
}

function render() {
}