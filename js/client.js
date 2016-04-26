function confirm(){
	console.log("client.js exists");
}

function returnBun(){
	return "Bun";
}

function confirm2(){
	console.log("confirm2");
}

function parseLotsJson(json){
	var dict = JSON.parse(json);
	for(var key in dict) {
		var value = dict[key];
		console.log(value);
		// do something with "key" and "value" variables
 
	}
}