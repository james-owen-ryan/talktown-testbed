//TODO: fix window arith
//FIX GAME SIZE
//THEN FIX COLLISION
// <|:-)
var gameSize = 1000;
/********************************************
*                                           *
*       parse and render lots               *
*                                           *
********************************************/
var preloadReady = false;

function parseLotsJson(json){
	var coordinates, xCoord, yCoord, dict, value;
	dict = JSON.parse(json);
	for(var key in dict) {
		value = dict[key];
		console.log(key, value);
		key = key.substring(1, key.length-1);
		coordinates = key.split(', ');
		xCoord = coordinates[0];
		yCoord = coordinates[1];
		renderLots(xCoord, yCoord, value);
	}
}

function renderLots(x, y, value){
	var width, height, posX, posY, building, scaleX, scaleY;
	width = ((x-0.625)*(gameSize/8))-(gameSize/16);
	height = ((y-0.625)*(gameSize/8))-(gameSize/16);
	posX = x.toString().substring(2, x.length);
	posY = y.toString().substring(2, y.length);
	if (value == "House") { 
		building = game.add.sprite(width, height, 'house');
	} else if (value == "NoneType") {
		building = game.add.sprite(width, height, 'empty_lot');
	} else {
		building = game.add.sprite(width, height, 'business');
	}

	game.physics.p2.enable(building);
	building.body.setRectangleFromSprite(building);

	building.body.static = true;
	building.body.immovable = true;
	
	scaleX = (gameSize/23)/building.width;	
	scaleY = (gameSize/23)/building.height;
	//depending on x and y, assign pivot and scale larger
	//set x anchor
	if (posX.valueOf() == "25") {
		building.anchor.x = 0.0;
	} else if (posX.valueOf() == "75") {
		building.anchor.x = 0.3;
	}
	//set y anchor
	if (posY.valueOf() == "25") {
		building.anchor.y = 0.0;
	} else if (posY.valueOf() == "75") {
		building.anchor.y = 0.3;
	}
	building.scale.setTo(scaleX,scaleY);

}


/********************************************
*                                           *
*       parse and render block              *
*                                           *
********************************************/


function parseBlocksJson(json){
	var coordinates, startX, startY, endX, endY, dir, list, length;
	list = JSON.parse(json);
	length = list.length;
	for (var i = 0; i < length; i++) {
		coordinates = list[i].split(', ');

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
	console.log("render blocks");
	console.log("start x is" + startX);
	var x, y, cont, block, scaleX, scaleY;
	x = ((startX-0.625)*(gameSize/8))-(gameSize/16);
	y = ((startY-0.625)*(gameSize/8))-(gameSize/16);
	cont = true;
	while (cont){
		block = game.add.sprite(x, y, 'block');
		scaleX = (gameSize/33)/block.width;	
		scaleY = (gameSize/33)/block.height;
		block.scale.setTo(scaleX,scaleY);
	
		if (dir == "v") {
			y += 1;
			if (y > ((endY-scaleX)*(gameSize/8))-(gameSize/16)) {
				cont = false;
			}
		} else if (dir == "h") {
			x += 1;
			if (x > ((endX-scaleY)*(gameSize/8))-(gameSize/16)) {
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
	game.load.image('player', 'Sprites/player.png');
	game.load.image('house', 'Sprites/house.png');
	game.load.image('empty_lot', 'Sprites/empty_lot.png');
	game.load.image('business', 'Sprites/business.png');
	game.load.image('block', 'Sprites/block.png');
}

var cursors;
var player;

function create() {
    //Define size of game world
    game.world.setBounds(0, 0, gameSize, gameSize);
	
	//Start physics system that enables player movement and colliders
	game.physics.startSystem(Phaser.Physics.P2JS);
	
    //Create a Group that will sit above the background image
    playerGroup = game.add.group();	

	//Add our player sprite to the world and allow it to move/collide
    player = game.add.sprite(game.world.centerX, game.world.centerY, 'player');
	game.physics.p2.enable(player);
	player.body.setRectangle(5,5);
	
	//Determines render order (player on top of blocks)
	playerGroup.add(player);

	//Keyboard input
    cursors = game.input.keyboard.createCursorKeys();

	//Camera
    game.camera.follow(player);

    //game.stage.backgroundColor = '#2d2d2d';

}
//Determine movement speed
var speed = 300;
function update() {
	//Render player on top
	game.world.bringToTop(playerGroup);
	
	//Set velocity and rotation to zero
    player.body.setZeroVelocity();
	player.body.setZeroRotation();

	//Check keyboard input and move accordingly
    if (cursors.up.isDown)
    {
		player.body.velocity.y = 0;
		player.body.velocity.y = -speed;
        //player.body.moveUp(speed)
    }
    else if (cursors.down.isDown)
    {
		player.body.velocity.x = 0;
		player.body.velocity.y = speed;
        //player.body.moveDown(speed);
    }

    if (cursors.left.isDown)
    {
		player.body.velocity.y = 0;
		//player.body.moveLeft(speed);
        player.body.velocity.x = -speed;
    }
    else if (cursors.right.isDown)
    {
		player.body.velocity.y = 0;
		player.body.velocity.x = speed;
        //player.body.moveRight(speed);
    }

}

function render() {
    game.debug.cameraInfo(game.camera, 32, 32);
    game.debug.spriteCoords(player, 32, 500);
}
