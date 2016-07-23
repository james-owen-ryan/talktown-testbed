var tracts_dict;

function parseTractsJson(json){

	tracts_dict = JSON.parse(json);
	for(var key in tracts_dict) {
		value = tracts_dict[key];
		console.log(key);
	}
	renderTracts();
}

function renderTracts(){
}