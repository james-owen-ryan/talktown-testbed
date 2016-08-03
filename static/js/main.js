var gameSize = 800;
//number to center the town
var center = gameSize/18;
var tileSize = gameSize/49;
//Determine movement speed
var speed = 310 ;
var cursors;
var player;
var building;
var tract;
var block;
var playerGroup;
var streetGroup;
var buildingGroup;

/********************************************
*                                           *
*       load house, empty ,and business     *
*       lots sprites                        *
*                                           *
********************************************/

function preload() {
	game.load.image('verBlock', 'Sprites/verBlock.png');
	game.load.image('horBlock', 'Sprites/horBlock.png');
	game.load.image("grass", "Sprites/grass.png");
	game.load.image('player', 'Sprites/player.png');
	game.load.image('house', 'Sprites/house.png');
	game.load.image('houseUL', 'Sprites/houseUL.png');
	game.load.image('houseLL', 'Sprites/houseLL.png');
	game.load.image('houseUR', 'Sprites/houseUR.png');
	game.load.image('houseLR', 'Sprites/houseLR.png');
	game.load.image('empty_lot', 'Sprites/empty_lot.png');
	game.load.image('tract', 'Sprites/tract.png');
	game.load.image('business', 'Sprites/business.png');
}


function create() {
	//Grass
	game.add.tileSprite(0, 0, window.innerWidth, window.innerHeight, 'grass');

	
	//Make a group for all the buildings
	buildingGroup = game.add.physicsGroup();
	
	//Make a group for all the streets
	streetGroup = game.add.physicsGroup();

    //Define size of game world
    game.world.setBounds(0, 0, window.innerWidth, window.innerHeight);

	
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


function update() {

	//Render player on top	
	game.world.bringToTop(buildingGroup);
	game.world.bringToTop(streetGroup);
	game.world.bringToTop(playerGroup);
		
		
	
	//Stop movement
    player.body.velocity.x = 0;
    player.body.velocity.y = 0;

	//Check keyboard input and move accordingly
    if (cursors.up.isDown) {
		player.body.velocity.x = 0;
		player.body.velocity.y = -speed;
		
    } else if (cursors.down.isDown) {
		player.body.velocity.x = 0;
		player.body.velocity.y = speed;
		
    } else if (cursors.left.isDown) {
		player.body.velocity.y = 0;
        player.body.velocity.x = -speed;
		
    } else if (cursors.right.isDown) {
		player.body.velocity.y = 0;
		player.body.velocity.x = speed;
    }
	
	checkHitBuilding();
		
}


function render() {
    game.debug.cameraInfo(game.camera, 32, 32);
    game.debug.spriteCoords(player, 32, 500);
}
