var i = 0;

/*
function parseLotsJson(json){
	var dict = JSON.parse(json);
	for(var key in dict) {
		var value = dict[key];
		console.log("["+key+value+"]");
		var sprite = game.add.sprite(i, 0, 'phaser');
		i = i + 30;
 
	}
}
*/
var coordinates;
var xCoord;
var yCoord;
var i = 1;
function parseLotsJson(json){
	var dict = JSON.parse(json);
	for(var key in dict) {
		var value = dict[key];
		console.log(key, value);
		//possibly remove quotes at beg and end of coords
		coordinates = key.split(', ');
		xCoord = coordinates[0].substring(1, coordinates[0].length - 1);
		yCoord = coordinates[1].substring(0, coordinates[1].length - 2);
		game.load.start()
		var sprite = game.add.sprite(xCoord*(window.innerWidth/12) + 5, yCoord*(window.innerHeight/12), 'house');
		//var sprite = game.add.sprite(i*(window.innerWidth/18), 30, 'phaser');}
		//i++;
		//console.log(i);
	}
}

function preload() {
	game.load.baseURL = 'http://examples.phaser.io/assets/';
	game.load.crossOrigin = 'anonymous';
	game.load.image('house', 'sprites/phaser-dude.png');
	


}
function create() {
}

function update() {
}

function render() {
}