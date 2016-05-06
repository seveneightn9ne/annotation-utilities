var fs = require('fs');

var make_sentences = function(file_data, file_corr_data) {

    // convert buffer to string
    var text = file_data.toString();
    // split into lines
    var lines = text.split('\n');

    // do the same thing for the corrected file data,
    // but first check if it's undefined
    if (!(file_corr_data == undefined)) {
        var text_corr = file_corr_data.toString();
        var lines_corr = text_corr.split('\n');
    } else {
        var lines_corr = [];
    }


    // split into lines

    var sentences = lines_to_sentences(lines, lines_corr);

    return sentences;

}

var search_sentences = function(phrase, error, language, sentences, callback) {
    var now = Date.now() / 1000;
    console.log("searching for phrase: "+phrase+". error: "+error);
    var matches = [];
    var pos_stats = {};
    var rel_stats = {};
    for(var i=0; i<sentences.length; i++) {
        var matches_in_sentence = sentences[i].matches(phrase, error, language);
        //console.log("Matches in sentence: "+JSON.stringify(matches_in_sentence));
        if(matches_in_sentence.length > 0) {
            matches.push({sentence:sentences[i], positions:matches_in_sentence});
            for(var j=0; j<matches_in_sentence.length; j++) {
                try {
                    var get_pos = sentences[i].get_pos(matches_in_sentence[j])
                } catch (err) {
                    continue;
                }
                if(pos_stats[get_pos] == undefined) {
                    pos_stats[get_pos] = 1;
                } else {
                    pos_stats[get_pos] = pos_stats[get_pos]+1;
                }
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
    callback(matches, stats);
}

var Sentence = function(lines) {
    this.fulltext = "";
    this.words = [];
    this.corrected;
    this.lang;
    this.sent_xml;
    for(var i=0; i<lines.length; i++) {
        // process lines[i]
        if(lines[i].charAt(0) == '#') {
            // it's a header line. process accordingly.
            if(lines[i].slice(0,5) == '#SENT') {
                sent_xml_initial = lines[i].slice(6);
                sent_xml_initial = sent_xml_initial.replace(/<ns type="/g, '<span class="error" title="');
                sent_xml_initial = sent_xml_initial.replace(/<\/ns>/g, '<\/span>');
                sent_xml_initial = sent_xml_initial.replace(/<i>/g, '<span class="err-orig">');
                sent_xml_initial = sent_xml_initial.replace(/<\/i>/g, '<\/span>');
                sent_xml_initial = sent_xml_initial.replace(/<c>/g, '<span class="err-corr">');
                sent_xml_initial = sent_xml_initial.replace(/<\/c>/g, '<\/span>');

                this.sent_xml = sent_xml_initial;
            } else if(lines[i].slice(0,3) == '#ID') {
                this.id = lines[i].slice(4);
            } else if(lines[i].slice(0,3) == '#L1') {
                this.lang = lines[i].slice(4);
            }
        } else {
            this.fulltext = this.fulltext.concat("\n"+lines[i]);
            this.words.push(new Word(lines[i]));
        }
    }

    sent = "";
    var punct = ['.', ',', '?', '!', "n't"];
    for(var i=0; i<this.words.length; i++) {
        if(punct.indexOf(this.words[i].word) == -1 && i>0) {
            sent += " ";
        }
        sent += this.words[i].word;
    }
    this.word_sentence = sent;

    this.get_pos = function(array) {
        pos_str = "";
        for (var i=0; i<array.length; i++) {
            if (array[i] == -1) continue;
            pos_str += this.words[array[i].index].pos;
            if(i<array.length-1) pos_str += " ";
        }
        return pos_str;
    }

    this.get_rel = function(array) {
        rel_str = "";
        for (var i=0; i<array.length; i++) {
            if (array[i] == -1) continue;
            rel_str += this.words[array[i].index].rel;
            if(i<array.length-1) rel_str += " ";
        }
        return rel_str;
    }

    this.matches = function (search_string, error, language) {
        var str_matches = false;
        var err_matches = false;
        var lang_matches = false;
        var all_matches = [];


        if ((error == "" || this.sent_xml == null) || this.sent_xml.indexOf('"'+error+'"') >= 0) {
            err_matches = true;
            //all_matches.push([[-1]]);
        }

        if (language == ""
            || this.lang == undefined
            || this.lang.toLowerCase() == language.toLowerCase()) {
            //console.log("LANGUAGE "+this.lang+" "+language);
            lang_matches = true;
        }

        if (search_string == "") {
            str_matches = true;
        } else {
            search_words = search_string.split(" ");
            for(var i=0; i<this.words.length-search_words.length; i++) {
                current_match = [];
                for (var j=0; j<search_words.length; j++) {
                    var match = this.words[i+j].matches(search_words[j]);
                    if(match=="false") {
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
        // console.log("======")
        // console.log("query: ("+search_string+") ("+error+") ("+language+")");
        // console.log(this.sent_xml)
        // console.log(this.lang)
        // console.log("str_matches: "+str_matches);
        // console.log("err_matches: "+err_matches);
        // console.log("lang_matches: "+lang_matches);
        // console.log("======")


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
    this.ptb_pos = line_items[4];
    this.h_ind = parseInt(line_items[6]);
    this.rel = line_items[7];

    this.toString = function() {
        return this.word;
    }

    this.matches = function(string) {
        if(string == string.toUpperCase() && string != "I") {
            if (string == this.pos || string == this.ptb_pos) {
                return "pos";
            }
        }
        if (string == this.rel) {
            return "rel";
        }
        var re = new RegExp("^"+string.toLowerCase()+"$");
        if(re.test(this.word.toLowerCase())) {
            return "word";
        }
        return "false";
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

//module.exports.do_search = do_search;
module.exports.make_sentences = make_sentences;
module.exports.search_sentences = search_sentences;
