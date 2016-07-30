function addBuildingPhysics(building){
	game.physics.enable(building, Phaser.Physics.ARCADE);
    building.body.immovable = true;
}


function addPlayerPhysics(){
	//Add our player sprite to the world and allow it to move/collide
    player = game.add.sprite(/*game.world.centerX, game.world.centerY*/0,0, 'player');
	//Scale the player sprite if needed
	player.scale.setTo(0.8,0.7);
	
	game.physics.arcade.enable(player);
	player.body.collideWorldBounds = true;


}