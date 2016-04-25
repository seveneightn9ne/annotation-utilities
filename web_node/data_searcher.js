var fs = require('fs');

var do_search = function(phrase, error, search_corpus, callback) {

	var output = [];

	if(search_corpus == "eng") {
		var corpus = "data/en-ud-train-1.2.conllu";
		var corpus_corr = "";

	} else {
		var corpus = "data/en_esl-ud.conllu";
		var corpus_corr = "data/en_cesl-ud.conllu";
	}

	fs.readFile(corpus, function(err, data) {

		// if there was an error, throw it (fix this later)
		if(err) throw err;

		search_file(phrase, error, data, corpus_corr, function(sentences) {
			callback(sentences);
		});

	});

};

var search_file = function(phrase, error, file_data, corr_filename, callback) {

		// convert buffer to string
		var text = file_data.toString();

		// split into lines
		var lines = text.split('\n');

		if(corr_filename != "") {
			fs.readFile(corr_filename, function(err, data) {

				// if there was an error, throw it (fix this later)
				if(err) throw err;

				var text = data.toString();
				var lines_corr = text.split('\n');
				var sentences = lines_to_sentences(lines, lines_corr);
				search_sentences(phrase, error, sentences, function(matches) {
					callback(matches);
				});

			});
		} else {
			// create sentences
			var sentences = lines_to_sentences(lines, []);
			search_sentences(phrase, error, sentences, function(matches) {
				callback(matches);
			});
		}

}

var search_sentences = function(phrase, error, sentences, callback) {
	var matches = [];
	for(var i=0; i<sentences.length; i++) {
		var matches_in_sentence = sentences[i].matches(phrase, error);
		if(matches_in_sentence.length > 0) {
			matches.push({sentence:sentences[i], positions:matches_in_sentence});
		}
	}
	callback(matches);

}

var Sentence = function(lines) {
	this.fulltext = "";
	this.words = [];
	this.corrected;
	for(var i=0; i<lines.length; i++) {
		// process lines[i]
		if(lines[i].charAt(0) == '#') {
			// it's a header line. process accordingly.
			if(lines[i].slice(0,5) == '#SENT') {
				sent_xml_initial = lines[i].slice(6);
				sent_xml_initial = sent_xml_initial.replace(/type="/g, 'class="error ');
				this.sent_xml = sent_xml_initial;
			} else if(lines[i].slice(0,3) == '#ID') {
				this.id = lines[i].slice(4);
			}
		} else {
			this.fulltext = this.fulltext.concat("\n"+lines[i]);
			this.words.push(new Word(lines[i]));
		}
	}

	this.matches = function (search_string, error) {
		var str_matches = false;
		var err_matches = false;
		var all_matches = [];
		if(this.sent_xml == undefined) {
			console.log("sent_xml undefined error: "+this.fulltext);
		}
		if (this.sent_xml.indexOf(error) >= 0) {
			err_matches = true;
			all_matches.push[[-1]];
		}
		if (search_string == "") {
			str_matches = true;
		} else {
			search_words = search_string.split(" ");
			for(var i=0; i<this.words.length-search_words.length; i++) {
				current_match = [];
				for (var j=0; j<search_words.length; j++) {
					if(!this.words[i+j].matches(search_words[j])) {
						break;
					}
					//console.log(this.words[i+j]+" matches "+search_words[j]);
					current_match.push(i+j);
					if(j==search_words.length-1) {
						str_matches = true;
						all_matches.push(current_match);
					}
				}
			}
		}
		return all_matches;
	}
}

var Word = function(line) {
	var all_pos = new Set(["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS",
			"PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN",
			"VBP","VBZ","WDT","WP","WP$","WRB","PUNCT"]);

	var all_upos = new Set(["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ","DET","NUM","PART",
			"PRON","SCONJ","PUNCT","SYM","X"]);

	var all_errors = new Set(["AGN","AGV","CL","CN","ID","IV","MA","MD","MT","MV","RA","RD","RJ","RN","RT",
			"RV","RY","UA","UD","UT","UV","TV","AGA","AGD","AGQ","AS","CD","CE","CQ","DA","DD","DV",
			"FD","FJ","FY","W","X","DJ","DN","DY","FN","FV","IJ","IN","IQ","L","MC","MJ","MN","MQ",
			"MY","RC","RQ","UC","UJ","UN","UQ","UY","AG","FQ","DQ","IY","FA","DI","IA","DT","UP","MP",
			"RP","S","SA","SX","M","R","U"]);

	var all_rel = new Set(["nsubj","nsubjpass","dobj","iobj","csubj","csubjpass","ccomp","xcomp","nummod",
			"appos","nmod","nmod:npmod","nmod:tmod","nmod:poss","acl","acl:relcl","amod","det",
			"det:predet","neg","case","advcl","advmod","compound","compound:prt","name",
			"mwe","foreign","goeswith","list","dislocated","parataxis","remnant","reparandum",
			"vocative","discourse","expl","aux","auxpass","cop","mark","punct","conj","cc","root",
			"cc:preconj","dep"]);

	var line_items = line.split("\t");
	this.word = line_items[1];
	this.pos = line_items[3];
	this.rel = line_items[7];

	this.toString = function() {
		return this.word;
	}

	this.matches = function(string) {
		if(string == string.toUpperCase() && string != "I") {
			return string == this.pos;
		}
		if (string == this.rel) {
			return true;
		}
		var re = new RegExp("^"+string+"$");
		return re.test(this.word);
	}

}

var lines_to_sentences = function(lines, lines_corr) {
	var sentences = [];
	var current_sentence = [];

	// create original sentences
	for(var i=0; i<lines.length; i++) {
		var line = lines[i].trim();
		if(line == "") {
			if(current_sentence.length > 0) {
				sentences.push(new Sentence(current_sentence));
				current_sentence = [];
			}
			continue;
		}
		current_sentence.push(line);
	}

	// create corrected sentences
	sentences_corr = {};
	var current_corr_sentence = [];
	for(var i=0; i<lines_corr.length; i++) {
		var line_corr = lines_corr[i].trim();
		if (line_corr == "") {
			if(current_corr_sentence.length > 0) {
				var new_corr_sentence = new Sentence(current_corr_sentence);
				sentences_corr[new_corr_sentence.id] = new_corr_sentence;
				current_corr_sentence = [];
			}
			continue;
		}
		current_corr_sentence.push(line_corr);
	}

	// match original sentences to corrected sentences
	if(lines_corr.length > 0) {
		for(var i=0; i<sentences.length; i++) {
			if (sentences[i] == undefined) {
				console.log("sentences[i] undefined error: i="+i);
			}
			if(sentences[i].id in sentences_corr) {
				sentences[i].corrected = sentences_corr[sentences[i].id];
			}
		}
	}

	return sentences;
}


module.exports.do_search = do_search;











