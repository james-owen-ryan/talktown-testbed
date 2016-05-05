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
	if (value == "House") { 
		var sprite = game.add.sprite(x*(window.innerWidth/9)-((window.innerWidth/9)/2),
									y*(window.innerHeight/9)-((window.innerHeight/9)/2),
									'house');
	} else if (value == "NoneType") {
		var sprite = game.add.sprite(x*(window.innerWidth/9)-((window.innerWidth/9)/2),
									y*(window.innerHeight/9)-((window.innerHeight/9)/2),
									'empty_lot');
	} else {
		game.add.sprite(x*(window.innerWidth/9)-((window.innerWidth/9)/2),
						y*(window.innerHeight/9)-((window.innerHeight/9)/2),
						'business');
	}
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
	}

}


//render json lots function
//render streets function



/********************************************
*                                           *
*       load house, empty ,and business     *
*       lots sprites                        *
*                                           *
********************************************/

function preload() {
	
	//game.load.baseURL = 'http://examples.phaser.io/assets/';
	//game.load.crossOrigin = 'anonymous';
	//game.load.image('empty_lot', 'sprites/phaser-dude.png');

	game.load.image('house', 'Sprites/house.png');
	game.load.image('empty_lot', 'Sprites/empty_lot.png');
	game.load.image('business', 'Sprites/business.png');
	preloadReady = true;

}
function create() {
}

function update() {
}

function render() {
}