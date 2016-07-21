function convert(num) {
	return ((num - 1) *(gameSize/9)) + center; 
	//subtract 1 to normalize the coordinates
}

function reconvert(num) {
	return ((num + 1)/(gameSize/9)) - center;
}
