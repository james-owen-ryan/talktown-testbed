var gameSize = 1200;
//number to center the town
var center = gameSize/26;
//Determine movement speed
var speed = 310 ;
var cursors;
var player;
var building;
var lots_dict;
var blocks_list;
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
		value = lots_dict[key] // value is treated as an array ?? perhaps json dicts keep intact
		type = value[0];
		key = key.substring(1, key.length-1);
		coordinates = key.split(', ');
		xCoord = coordinates[0];
		yCoord = coordinates[1];
		renderLots(xCoord, yCoord, type);
	}
}

function renderLots(xCoord, yCoord, value){
	var x, y, tmpX, tmpY, scaleX, scaleY;
	
	//subtract 1 to normalize the coordinates
	x = xCoord - 1;
	y = yCoord - 1;	
	x = (x*(gameSize/9)) + center;
	y = (y*(gameSize/9)) + center;

	if (value == "House") { 
		building = game.add.sprite(x, y, 'house');
	} else if (value == "NoneType") {
		building = game.add.sprite(x, y, 'empty_lot');
	} else {
		building = game.add.sprite(x, y, 'business');
	}
	
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
	addBuildingPhysics();
	
}

function addBuildingPhysics(){
	game.physics.enable(building, Phaser.Physics.ARCADE);
    building.body.immovable = true;
}


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
		
	// block number * unit size + center
	// the reason the unit is 1/9 of gamesize and not 1/8
	// is because the last block will be cut off otherwise.
	// instead, we are left with extra space that we deal with 
	// using "center"
	
	startingBlockX = startX - 1;
	startingBlockY = startY - 1;
	endingBlockX = endX - 1;
	endingBlockY = endY - 1;
	
	x = (startingBlockX*(gameSize/9))+center;
	y = (startingBlockY*(gameSize/9))+center;
	
	cont = true;
	while (cont){
	
		if (dir == "v") {
			block = game.add.sprite(x, y, 'verBlock');
			y += 1;
			if (y > (endingBlockY*(gameSize/9))+center) {
				cont = false;
			}
		} else if (dir == "h") {
			block = game.add.sprite(x, y, 'horBlock');
			x += 1;
			if (x > (endingBlockX*(gameSize/9))+center) {
				cont = false;
			}
		}
	// scale blocks smaller than buildings
	scaleX = (gameSize/33)/block.width;	
	scaleY = (gameSize/33)/block.height;
	block.scale.setTo(scaleX,scaleY);

	}	
}

/********************************************
*                                           *
*       load house, empty ,and business     *
*       lots sprites                        *
*                                           *
********************************************/

function preload() {
	game.load.image("background", "Sprites/grass.png");
	game.load.image('player', 'Sprites/player.png');
	game.load.image('house', 'Sprites/house.png');
	game.load.image('empty_lot', 'Sprites/empty_lot.png');
	game.load.image('business', 'Sprites/business.png');
	game.load.image('verBlock', 'Sprites/verBlock.png');
	game.load.image('horBlock', 'Sprites/horBlock.png');
}


function create() {
	//Make a group for all the buildings
	buildingGroup = game.add.physicsGroup();

    //Define size of game world
    game.world.setBounds(0, 0, gameSize, gameSize);

	//Grass
	game.add.tileSprite(0, 0, gameSize, gameSize, 'background');
	
	//Keyboard input
    cursors = game.input.keyboard.createCursorKeys();
	
	//Create a group for player that will sit above the background image
    playerGroup = game.add.group();	

	//Start physics system that enables player movement and colliders
	game.physics.startSystem(Phaser.Physics.ARCADE);
	addPlayerPhysics();

	//Add player to its own group
	playerGroup.add(player);

	//Camera
    game.camera.follow(player);


}

function addPlayerPhysics(){
	//Add our player sprite to the world and allow it to move/collide
    player = game.add.sprite(/*game.world.centerX, game.world.centerY*/0,0, 'player');
	//Scale the player sprite if needed
	player.scale.setTo(0.8,0.7);
	
	game.physics.arcade.enable(player);
	player.body.collideWorldBounds = true;


}

function update() {
	
	//Render player on top
	game.world.bringToTop(buildingGroup);
	game.world.bringToTop(playerGroup);

	checkHitBuilding();
		
	//Stop movement
    player.body.velocity.x = 0;
    player.body.velocity.y = 0;

	//Check keyboard input and move accordingly
    if (cursors.up.isDown)
    {
		player.body.velocity.x = 0;
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

function checkHitBuilding(){
	if (game.physics.arcade.collide
			(player, buildingGroup)){

			console.log('boom');
	}
}


function render() {
    game.debug.cameraInfo(game.camera, 32, 32);
    game.debug.spriteCoords(player, 32, 500);
}
