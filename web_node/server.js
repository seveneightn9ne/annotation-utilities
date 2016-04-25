var http = require('http');
var express = require('express'), 
	app = express();
var searcher = require('./data_searcher');

/*var server = http.createServer(function(req, res) {
	res.writeHead(200);
	res.end('Hello Http');
});
server.listen(8080);*/

app.use(express.static(__dirname + '/public'));

app.get('/search', function (req, res) {
    //res.send(req.query);
    console.log(req.query.query);
    searcher.do_search(req.query.query, req.query.error, req.query.corpus, function(matches) {
    	res.send({"query":req.query, "matches": matches});
    	console.log("returned result");
    });
    console.log("GET /search");
});

app.listen(8080);