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
    if(req.query.corpus == "esl") {
        var corpus = data_sources["esl_sentences"];
    } else {
        var corpus = data_sources["eng_sentences"]
    }
    searcher.search_sentences(req.query.query, req.query.error, corpus, function(matches, stats) {
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
        fs.readFile(esl_corpus.corr,
            function(err, data2) {
                var esl_sentences = searcher.make_sentences(data1, data2);
                data_sources["esl_sentences"] = esl_sentences;

                fs.readFile(eng_corpus.main, function(err, data) {
                    var eng_sentences = searcher.make_sentences(data, undefined);
                    data_sources["eng_sentences"] = eng_sentences;
                    app.listen(8888);
                });
        });
});



