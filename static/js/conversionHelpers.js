// ** coding has changed since v		
	// block number * unit size + center
	// the reason the unit is 1/9 of gamesize and not 1/8
	// is because the last block will be cut off otherwise.
	// instead, we are left with extra space that we deal with 
	// using "center"
	

function convert(num) {
	return ((num - 1) *(gameSize/9)) + center; 
	//subtract 1 to normalize the coordinates
}

function reconvert(num) {
	return ((num + 1)/(gameSize/9)) - center;
}
