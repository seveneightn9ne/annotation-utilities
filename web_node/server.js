/*
 * THIS IS THE MAIN JAVASCRIPT FILE FOR THE SERVER.
 * To run, navigate to this directory and type the command
 *
 * node server.js
 *
 * First it will run the sentence initialization function (see below).
 * Right now, that takes about 10 seconds. Once that completes,
 * the server will print "Starting server" and begin serving files.
 * Until that point, the site will not load.
 *
 */

// Includes
var http = require('http');
var express = require('express'), 
	app = express();
var fs = require('fs');
var searcher = require('./data_searcher');

// Paths to corpus file locations
var eng_corpus = {main:"data/en-ud-1.4.conllu", corr:""};
var esl_corpus = {main:"data/en_esl-ud.conllu", corr:"data/en_cesl-ud.conllu"};

// Set directory that the server will serve
app.use(express.static(__dirname + '/public'));

// Function that runs when an AJAX call is made to /search
app.get('/search', function (req, res) {

    // Log query to file
    var logstr = (new Date).toString() + " " + JSON.stringify(req.query) + "\n";
    fs.appendFile('searches.log', logstr, function (err) {});

    console.log(logstr);

    // Set which corpus to search
    if(req.query.corpus == "esl") {
        var corpus = data_sources["esl_sentences"];
    } else {
        var corpus = data_sources["eng_sentences"]
    }

    // Call search function
    searcher.search_sentences(req.query.query, req.query.error, req.query.language, corpus, function(matches, stats) {
        // Callback function that runs when search is finished
        // Send search results back to client
        res.send({"query":req.query, "stats":stats, "matches": matches});
        console.log("returned result");
    });
    console.log("GET /search");
});


// Initialize sentence objects by reading corpus files.
// This code runs when the server starts up, and the server
// doesn't begin serving files until the function is complete.
var data_sources = {};
fs.readFile(esl_corpus.main,
    function(err, data1) {
        if (err) throw err;
        fs.readFile(esl_corpus.corr,
            function(err, data2) {
                if (err) throw err;
                if(data1 == undefined) {
                    console.log(esl_corpus.main+"is missing");
                }
                if(data2 == undefined) {
                    console.log(esl_corpus.corr+"is missing");
                }
                var esl_sentences = searcher.make_sentences(data1, data2);
                data_sources["esl_sentences"] = esl_sentences;

                fs.readFile(eng_corpus.main, function(err, data) {
                    var eng_sentences = searcher.make_sentences(data, undefined);
                    data_sources["eng_sentences"] = eng_sentences;
                    // When the following line prings, the server is ready
                    console.log("Starting server");
                    app.listen(80);
                });
        });
});



