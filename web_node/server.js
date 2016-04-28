var http = require('http');
var express = require('express'), 
	app = express();
var fs = require('fs');
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
    /*searcher.do_search(req.query.query, req.query.error, req.query.corpus, function(matches, stats) {
    	res.send({"query":req.query, "stats":stats, "matches": matches});
    	console.log("returned result");
    });*/
    searcher.search_sentences(req.query.query, req.query.error, data_sources["esl_sentences"], function(matches, stats) {
        res.send({"query":req.query, "stats":stats, "matches": matches});
        console.log("returned result");
    });
    console.log("GET /search");
});

var eng_corpus = {main:"data/en-ud-train-1.2.conllu", corr:""};
var esl_corpus = {main:"data/en_esl-ud.conllu", corr:"data/en_cesl-ud.conllu"};

var data_sources = {};
fs.readFile(esl_corpus.main,
    function(err, data1) {
        data_sources[esl_corpus.main] = data1;
        fs.readFile(esl_corpus.corr,
            function(err, data2) {
                data_sources[esl_corpus.corr] = data2;
                var esl_sentences = searcher.make_sentences(data1, data2);
                data_sources["esl_sentences"] = esl_sentences;
                app.listen(8888);
            })
    });

