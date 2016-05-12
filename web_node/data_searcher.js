// This file contains all of the actual search logic

// Includes
var fs = require('fs');

// Takes raw corpus file data as input, and returns a list of sentence objects
var make_sentences = function(file_data, file_corr_data) {

    // Convert data buffer to string
    var text = file_data.toString();
    // Split into lines
    var lines = text.split('\n');

    // Do the same thing for the corrected file data,
    // but first check if it's undefined
    // (might be undefined if we're reading the English corpus files,
    //  which don't have a corrected version)
    if (!(file_corr_data == undefined)) {
        var text_corr = file_corr_data.toString();
        var lines_corr = text_corr.split('\n');
    } else {
        var lines_corr = [];
    }

    // Convert lines to sentences
    var sentences = lines_to_sentences(lines, lines_corr);

    return sentences;

}

// Takes as input all the query information, plus a list of Sentence objects,
// performs the search, and calls the callback function when finished.
var search_sentences = function(phrase, error, language, sentences, callback) {

    console.log("Searching for phrase: "+phrase+". error: "+error);

    var matches = [];
    var pos_stats = {};
    var rel_stats = {};

    // Loop through and search each sentence
    for(var i=0; i<sentences.length; i++) {

        // sentence.matches returns a list of matches in that sentence,
        // or an empty list if therer are no matches.
        var matches_in_sentence = sentences[i].matches(phrase, error, language);

        // If there is a match
        if(matches_in_sentence.length > 0) {

            // Add sentence to list of matching sentences
            matches.push({sentence:sentences[i], positions:matches_in_sentence});

            // Compile stats for sentence
            for(var j=0; j<matches_in_sentence.length; j++) {

                // If the index of the match is -1 (which is the case when the 
                // search matches an error, which doesn't have a particular index,
                // or when it matches the source language), then get_pos will fail.
                // Catch this error and continue if this is the case.
                try {
                    var get_pos = sentences[i].get_pos(matches_in_sentence[j])
                } catch (err) {
                    continue;
                }

                // Store counts of each pattern in dictionary
                if(pos_stats[get_pos] == undefined) {
                    pos_stats[get_pos] = 1;
                } else {
                    pos_stats[get_pos] = pos_stats[get_pos]+1;
                }

                // Do the same thing for get_rel
                var get_rel = sentences[i].get_rel(matches_in_sentence[j])
                if(rel_stats[get_rel] == undefined) {
                    rel_stats[get_rel] = 1;
                } else {
                    rel_stats[get_rel] = rel_stats[get_rel]+1;
                }
            }
        }
    }
    var stats = {rel: rel_stats, pos: pos_stats};

    // Call the callback function, passing along the results and the stats
    callback(matches, stats);
}

// Sentence object represents a single sentence in the corpus
var Sentence = function(lines) {
    this.fulltext = "";
    this.words = [];
    this.corrected;
    this.lang;
    this.sent_xml;

    // Sentence constructor (takes a list of lines as input)
    // Loop through each line to process it
    for(var i=0; i<lines.length; i++) {

        // If it begins with '#', it's a header line
        if(lines[i].charAt(0) == '#') {

            // #SENT is the sentence XML line with errors annotated
            if(lines[i].slice(0,5) == '#SENT') {
                // Do a bunch of regex replaces to turn this into a valid HTML string
                // that we can plunk right into the webpage
                sent_xml_initial = lines[i].slice(6);
                sent_xml_initial = sent_xml_initial.replace(/<ns type="/g, '<span class="error" title="');
                sent_xml_initial = sent_xml_initial.replace(/<\/ns>/g, '<\/span>');
                sent_xml_initial = sent_xml_initial.replace(/<i>/g, '<span class="err-orig">');
                sent_xml_initial = sent_xml_initial.replace(/<\/i>/g, '<\/span>');
                sent_xml_initial = sent_xml_initial.replace(/<c>/g, '<span class="err-corr">');
                sent_xml_initial = sent_xml_initial.replace(/<\/c>/g, '<\/span>');
                this.sent_xml = sent_xml_initial;

            // #ID is the sentence id code. We use this to match up the original sentences
            // to the corrected sentences.
            } else if(lines[i].slice(0,3) == '#ID') {
                this.id = lines[i].slice(4);

            // #L1 is the first language of the sentence writer. This is one of the
            // variables that can be searched for.
            } else if(lines[i].slice(0,3) == '#L1') {
                this.lang = lines[i].slice(4);
            }

        // If it's not a line that begins with #, it's part of the sentence text itself.
        } else {
            this.fulltext = this.fulltext.concat("\n"+lines[i]);
            this.words.push(new Word(lines[i]));
        }
    }

    // Construct a string representation of the sentence
    sent = "";
    var punct = ['.', ',', '?', '!', "n't"];
    for(var i=0; i<this.words.length; i++) {
        if(punct.indexOf(this.words[i].word) == -1 && i>0) {
            sent += " ";
        }
        sent += this.words[i].word;
    }
    this.word_sentence = sent;

    // Takes as input an array of indices,
    // and returns a string consisting of
    // the concatenated parts of speech
    // of the words at those indices
    this.get_pos = function(array) {
        pos_str = "";
        for (var i=0; i<array.length; i++) {
            if (array[i] == -1) continue;
            pos_str += this.words[array[i].index].pos;
            if(i<array.length-1) pos_str += " ";
        }
        return pos_str;
    }

    // (Same as get_pos, but for relations)
    // Takes as input an array of indices,
    // and returns a string consisting of
    // the concatenated relations
    // of the words at those indices
    this.get_rel = function(array) {
        rel_str = "";
        for (var i=0; i<array.length; i++) {
            if (array[i] == -1) continue;
            rel_str += this.words[array[i].index].rel;
            if(i<array.length-1) rel_str += " ";
        }
        return rel_str;
    }

    // Takes as input:
    //   - a search string (may be empty)
    //   - an error type to search for (may be empty)
    //   - a language to search for (may be empty)
    // and returns a list of matches for the given query in the sentence.
    //
    // Each match is a dictionary of the form {index: number, what: match_type},
    // where number is a number representing the word number of the match in the sentence,
    // and match_type is a string representing what was matched. Match_type
    // may be "pos", "rel", "word" or "other".
    //
    // If the search matches something that doesn't have a particular index
    // in the sentence (i.e. an error, which may span multiple words, or apply to the whole sentence),
    // or the first language of the writer), index will be -1 and match_type will be "other".
    this.matches = function (search_string, error, language) {

        var str_matches = false;
        var err_matches = false;
        var lang_matches = false;
        var all_matches = [];

        // If the error type is not specified in the query, OR the sentence doesn't have error information,
        // OR the error is specified and it appears in the sentence, we have an error match.
        if ((error == "" || this.sent_xml == null) || this.sent_xml.indexOf('"'+error+'"') >= 0) {
            err_matches = true;
            //all_matches.push([[-1]]);
        }

        // If the language is not specified in the query, OR the sentence doesn't have language information,
        // OR the language is specified and it matches the sentence, we have a language match.
        if (language == ""
            || this.lang == undefined
            || this.lang.toLowerCase() == language.toLowerCase()) {
            //console.log("LANGUAGE "+this.lang+" "+language);
            lang_matches = true;
        }

        // If there is no query string, trivially, it matches.
        if (search_string == "") {
            str_matches = true;
        // Otherwise, see if it matches the sentence consecutively.
        } else {
            search_words = search_string.split(" ");
            for(var i=0; i<this.words.length-search_words.length; i++) {
                current_match = [];
                for (var j=0; j<search_words.length; j++) {
                    var match = this.words[i+j].matches(search_words[j]);
                    if(!match) {
                        break;
                    }
                    current_match.push({index:i+j, what:match});
                    if(j==search_words.length-1) {
                        str_matches = true;
                        all_matches.push(current_match);
                    }
                }
            }
        }


        if(str_matches && err_matches && lang_matches) {
            if(all_matches.length == 0) {
                all_matches.push([[{index:-1, what:"other"}]]);
            }
            return all_matches;
        } else {
            return [];
        }
    }
}

// Class representing a single word in a sentence, containing all the information
// about that word (such as rel and pos)
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

    // Create the word, given a line from a CONLLU annotation
    var line_items = line.split("\t");
    this.word = line_items[1];
    this.pos = line_items[3];
    this.ptb_pos = line_items[4];
    this.h_ind = parseInt(line_items[6]);
    this.rel = line_items[7];

    this.toString = function() {
        return this.word;
    }

    // Matching function
    // Returns a string indicating the type of match, or false if there is no match
    this.matches = function(string) {
        // If string is all-caps and not "I" (lol) then try to match it to
        // the part of speech
        if(string == string.toUpperCase() && string != "I") {
            if (string == this.pos || string == this.ptb_pos) {
                return "pos";
            }
        }
        // Try to match it 
        if (string == this.rel) {
            return "rel";
        }
        var re = new RegExp("^"+string.toLowerCase()+"$");
        if(re.test(this.word.toLowerCase())) {
            return "word";
        }
        return false;
    }

}

// Function that takes as input
//  - a bunch of lines (i.e. from a corpus file)
//  - (optionally) a bunch of lines from the corresponding corrected version of the sentences
// and returns a list of Sentence objects generated from those lines
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

// Public functions (called by server.js)
module.exports.make_sentences = make_sentences;
module.exports.search_sentences = search_sentences;
