var fs = require('fs');
var another = require('./another_test');

var do_a_thing = function(callback) {

	var variable = "this is a string you should know"

	fs.readFile("random.txt", function(err, data) {

		if (err) console.log(err);

		var text = data.toString();

		callback([text, variable]);

	});

	another.do_emily("bananas");

};

do_a_thing(function(list){
	for(var i=0; i<list.length; i++) {
		console.log(list[i]);
	}
});