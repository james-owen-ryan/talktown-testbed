//TODO: fix window arith
var gameSize = 1000;
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
	var width = ((x-0.625)*(gameSize/8))-(gameSize/16);
	var height = ((y-0.625)*(gameSize/8))-(gameSize/16);
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

	var scaleX = (gameSize/23)/sprite.width;	
	var scaleY = (gameSize/23)/sprite.height;
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
	var list = JSON.parse(json);

	
	var listLength = list.length;
	for (var i = 0; i < listLength; i++) {
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
	var x = ((startX-0.625)*(gameSize/8))-(gameSize/16);
	var y = ((startY-0.625)*(gameSize/8))-(gameSize/16);
	var cont, sprite, scaleX, scaleY;
	cont = true;
	while (cont){
		sprite = game.add.sprite(x, y, 'block');
		scaleX = (gameSize/33)/sprite.width;	
		scaleY = (gameSize/33)/sprite.height;
		sprite.scale.setTo(scaleX,scaleY);
	
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
    //  Create a Group that will sit above the background image
    group1 = game.add.group();
	
    //game.stage.backgroundColor = '#2d2d2d';

    //  Make our game world gameSizexgameSize pixels in size (the default is to match the game size)
    game.world.setBounds(0, 0, gameSize, gameSize);


	game.physics.startSystem(Phaser.Physics.P2JS);

    player = game.add.sprite(game.world.centerX, game.world.centerY, 'player');
	group1.add(player);
    game.physics.p2.enable(player);

    cursors = game.input.keyboard.createCursorKeys();

    game.camera.follow(player);


}

function update() {
	game.world.bringToTop(group1);
    player.body.setZeroVelocity();

    if (cursors.up.isDown)
    {
		player.body.velocity.y = 0;
		player.body.velocity.y = -300;
        //player.body.moveUp(300)
    }
    else if (cursors.down.isDown)
    {
		player.body.velocity.x = 0;
		player.body.velocity.y = 300;
        //player.body.moveDown(300);
    }

    if (cursors.left.isDown)
    {
		player.body.velocity.y = 0;
		//player.body.moveLeft(300);
        player.body.velocity.x = -300;
    }
    else if (cursors.right.isDown)
    {
		player.body.velocity.y = 0;
		player.body.velocity.x = 300;
        //player.body.moveRight(300);
    }

}

function render() {

    game.debug.cameraInfo(game.camera, 32, 32);
    game.debug.spriteCoords(player, 32, 500);
}
/*

	preloadReady = true;

}
var player;
function create() {
	game.world.setBounds(0, 0, 400, 400);

    game.physics.startSystem(Phaser.Physics.P2JS);

    player = game.add.sprite(game.world.centerX, game.world.centerY, 'player');

    game.physics.p2.enable(player);

    cursors = game.input.keyboard.createCursorKeys();

    game.camera.follow(player);

}

function update() {

    player.body.setZeroVelocity();

    if (cursors.up.isDown)
    {
        player.body.moveUp(300)
    }
    else if (cursors.down.isDown)
    {
        player.body.moveDown(300);
    }

    if (cursors.left.isDown)
    {
        player.body.velocity.x = -300;
    }
    else if (cursors.right.isDown)
    {
        player.body.moveRight(300);
    }

}

function render() {

    game.debug.cameraInfo(game.camera, 32, 32);
    game.debug.spriteCoords(player, 32, 500);

}*/