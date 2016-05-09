
// Logic.js contains all front-end Javascript functionality.
// It mainly deals with formatting and inserting the HTML for
// the search results returned from the server.


// Dictionary of error codes mapped to their full name
var error_names = {
    "AGN":"Noun agreement",
    "AGV":"Verb agreement",
    "AGA":"Pronoun agreement",
    "AGD":"Determiner agreement",
    "AGQ":"Quantifier agreement",
    "AS":"Argument structure",
    "CL":"Collocation",
    "CE":"Compound",
    "CD":"Countability determiner",
    "CN":"Countability noun",  
    "CQ":"Countability quantifier",
    "DJ":"Adjective derivation",
    "DY":"Adverb derivation",
    "DD":"Determiner derivation",
    "DN":"Noun derivation",
    "DT":"Preposition derivation",
    "DA":"Pronoun derivation",
    "DQ":"Quantifier derivation",
    "DV":"Verb derivation",
    "FJ":"Adjective form",
    "FY":"Adverb form",
    "FD":"Determiner form",
    "FN":"Noun form",
    "FA":"Pronoun form",
    "FQ":"Quantifier form",
    "FV":"Verb form",
    "IJ":"Adjective formation",
    "IY":"Adverb formation",
    "ID":"Determiner formation",
    "X":"Negation formation",
    "IN":"Noun formation",
    "IA":"Pronoun formation",
    "IQ":"Quantifier formation",
    "IV":"Verb formation",  
    "MJ":"Missing adjective",
    "MY":"Missing adverb",
    "MC":"Missing conjunction",
    "MD":"Missing determiner",
    "MN":"Missing noun",
    "MT":"Missing preposition",
    "MA":"Missing pronoun",
    "MP":"Missing punctuation",
    "MQ":"Missing quantifier",
    "MV":"Missing verb",
    "L":"Register",
    "RJ":"Replace adjective",
    "RY":"Replace adverb",
    "RC":"Replace conjunction",
    "RD":"Replace determiner",
    "RN":"Replace noun",
    "RT":"Replace preposition",
    "RQ":"Replace quantifier",
    "RA":"Replace pronoun",
    "RP":"Replace punctuation",
    "RV":"Replace verb",
    "S":"Spelling",
    "SA":"Spelling (American)",
    "SX":"Spelling confusion",
    "TV":"Verb tense",
    "UJ":"Unnecessary adjective",
    "UY":"Unnecessary adverb",
    "UC":"Unnecessary conjunction",
    "UD":"Unnecessary determiner",
    "UN":"Unnecessary noun",
    "UT":"Unnecessary preposition",
    "UA":"Unnecessary pronoun",
    "UP":"Unneccessary punctuation",
    "UQ":"Unnecessary quantifier",
    "UV":"Unnecessary verb",              
    "W":"Word order"
};

// Initializes error name popups
$(function() {
    $( document ).tooltip({
    position: { my: "bottom", at: "top-10" }
    });
});

// Triggered when the user hits the Search button (or hits return)
function do_search(event) {

    // Empty out the results div
    $('#results').empty();

    // Get values from all menus and text boxes
    var query = document.getElementById("search_field").value;
    var error = document.getElementById("error").value;
    var language = document.getElementById("language").value;
    var corpus = document.getElementById("corpus_list").value;
    var show_corr = document.getElementById("corr").checked && corpus=="esl";
    var hl_err = document.getElementById("hl_err").checked;

    // Put a "searching..." message in the results div while results are being gathered
    $('#results').append("<p>Searching for <b>"+query+"</b>...</p>");   

    // Form AJAX request to server
    var ajax_url = "/search?query="+encodeURIComponent(query)+"&corpus="+corpus+"&error="+error+"&language="+language;
    $.get(ajax_url, success=function(response){
         // Callback function -- runs when AJAX result is returned

         // Empty results div
         $('#results').empty();

         // Put results in div
         $('#results').append(format_response(response, show_corr, hl_err));

         // Make sure tooltips work
         $(".error").addClass("tooltip");

         // Insert placeholders for "missing" errors
         format_errors();

         // Trigger Annodoc to generate visualizations
         Annodoc.activate(Config.bratCollData, documentCollections);
    });
}

// Hides add'l search options if English treebank is selected
function update_filter_visibility(value) {
    if(value == "esl") {
        $("#filters").css("display", "inline");
    } else {
        $("#filters").css("display", "none");
    }
}

// Inserts placeholder icons for "missing" errors,
// and makes error popups show the full error name
// instead of the abbreviated error code
function format_errors() {

    // For each span with id "error" (all errors)
    $('.error').each(function(index){
        // Replace the title text (error code) with the full error name
        // Uses error name dictionary defined at top of file
        $(this).prop('title', error_names[$(this).attr('title')]);
    });

    // For each span with id "error"
    $('.error').each(function(index) {
        // If the span contains no "original error" span but does contain a "corrected error span"
        if($(this).find('.err-orig').length == 0 && $(this).find('.err-corr').length == 1) {
            // Append a placeholder icon
            $(this).append('<span class="err-orig no-background"><img class="missing" src="/images/missing.png"></img></span>')
        }});
}

// If user hits return key, submit
function checkSubmit(e) {
    if(e && e.keyCode == 13) {
        document.getElementById("search_button").click();
    }
}

// Takes stats object as input
// and returns formatted HTML of stats table
function format_stats_section(stats) {
    html_string = "";
    html_string += '<table id="stats_table">';
    html_string += '<tr><td><u>Parts of speech</u></td><td width="20px"></td><td><u>Relations</u></td></tr>';
    html_string += '<tr><td>';
    html_string += format_stats_table(stats.pos);
    html_string += '</td><td></td><td>';
    html_string += format_stats_table(stats.rel);
    html_string += '</td></tr></table>';
    return html_string;
}

// Takes as input one individual part of the stats object
// and returns formatted HTML table of the results for that stat
function format_stats_table(stats_object) {
    var html_string = '';
    var stats_array = arrayify_and_sort(percentify(stats_object));
    html_string += '<table>';
    for(var i=0; i<stats_array.length; i++) {
        html_string += '<tr><td>'+stats_array[i].key+'</td><td width="10px"></td><td>'+stats_array[i].value+'%</td></tr>';
    }
    html_string += '</table>';
    return html_string;
}

// Takes as input a dictionary of the form { category1:value1, category2,value2, ... }
// and returns the same dictionary with the values converted to percentages (on a 1-100 scale)
function percentify(number_dict) {
    var total = sum_dict(number_dict);
    var percentified_dict = {};
    for (var item in number_dict) {
        percentified_dict[item] = (Math.round(number_dict[item]/total*1000)/10);
    }
    return percentified_dict;
}

// Takes as input a dictionary of the form { key1:value1, key2:value2, ... }
// and converts it to an array of the form [ { key:key1, value:value1 }, { key:key2, value:value2 } ],
// then sorts it by value and returns the sorted array
function arrayify_and_sort(number_dict) {
    var my_array = [];
    for(var item in number_dict) {
        my_array.push({"key":item, "value":number_dict[item]});
    }
    my_array = my_array.sort(function(a,b) { 
        return b.value - a.value;
    });
    return my_array;
}

// Takes as input a dictionary of the form { key1:value1, key2:value2, ... }
// and returns the sum of all the values
function sum_dict(my_dict) {
    var total = 0;
    for (var item in my_dict) {
        total += my_dict[item];
    }
    return total;
}

// Given a sentence object, a list of indices where the word matches the search,
// and a boolean representing whether we want to highlight errors,
// return an appropriate HTML string displaying the text of the sentence
function sentence_text(sentence, match_indices, hl_err) {

    html_string = "";

    // If we want to highlight errors, we should use the sentence's
    // XML string, if available
    if(hl_err) {
        if(sentence.sent_xml != undefined) {
            html_string += sentence.sent_xml;
        } else {
            html_string += sentence.word_sentence;
        }

    // Otherwise, we will construct a string that highlights the search matches
    } else {
        for(var j=0; j<sentence.words.length; j++) {
            if(match_indices.indexOf(j) >= 0) {
                html_string += '<span class="match">' + sentence.words[j].word + '</span> ';
            } else {
                html_string += sentence.words[j].word + ' ';
            }
        }
    }

    return html_string;
}

// Master function that takes as input
//      - the AJAX response object (representing the search results)
//      - whether to show the corrected version of the sentence below the original (bool)
//      - whether to highlight errors in the sentence (bool)
// and returns a formatted HTML string containing the search results
function format_response(response, show_corr, hl_err) {

    // Max number of results to return. Deliberately set high so that
    // results will not be limited -- make lower to induce limiting.
    var max_results = 10000;
    var html_string = "";
    var corpus_names = {esl:"ESL", eng:"English"};
    
    // Insert header row indicating number of results
    html_string += "<p><b>"+response.matches.length+"</b> matching sentences for <em>"+response.query.query+"</em> in the "+corpus_names[response.query.corpus]+" corpus.</p>";
    
    // Insert stats table
    html_string += '<div id="stats">';
    html_string += format_stats_section(response.stats);
    html_string += "</div>";

    // Insert each result
    for(var i=0; i<Math.min(response.matches.length, max_results); i++) {

        html_string += '<div class="result">';

        // Generate list of indices of matching words in the sentence
        var match_positions = [].concat.apply([], response.matches[i].positions);
        var match_indices = [];
        for(var x=0; x<match_positions.length; x++) {
            match_indices.push(match_positions[x].index);
        }
        
        // Insert sentence text
        html_string += '<span class="sent-orig">';
        html_string += sentence_text(response.matches[i].sentence, match_indices, hl_err);
        html_string += '</span>';

        // Build list of formatting commands for Annodoc
        var tree_highlights = ["# sentence-label "+(i+1)];
        for(var j=0; j<match_positions.length; j++) {
            if(match_positions[j].what == "word") {
                tree_highlights.push('# visual-style '+(match_positions[j].index+1)+' bgColor:#fff59d');
            } else if(match_positions[j].what == "pos") {
                tree_highlights.push('# visual-style '+(match_positions[j].index+1)+' bgColor:#fff59d');
            } else if(match_positions[j].what == "rel") {
                tree_highlights.push('# visual-style '+(response.matches[i].sentence.words[match_positions[j].index].h_ind)+' '+(match_positions[j].index+1)+' '+response.matches[i].sentence.words[match_positions[j].index].rel+' color:#D1C113');
            }
        }

        // Insert sentence in CONLLU format (for Annodoc to display)
        html_string += wrap_sentence_fulltext(tree_highlights.join("\n")+response.matches[i].sentence.fulltext);
        
        // If we want to show the corrected version of the sentence, insert it
        if(show_corr) {
            html_string += '<span class="sent-corr">';
            html_string += sentence_text(response.matches[i].sentence, match_indices,true);
            html_string += '</span>';
            html_string += wrap_sentence_fulltext("# sentence-label "+(i+1)+response.matches[i].sentence.corrected.fulltext);
        }

        html_string += '</div>';
    }

    return html_string;
}

// Wraps sentence fulltext in CONLLU tags
function wrap_sentence_fulltext(text) {
    return '<pre><code class="language-conllu">'+text+'\n\n</code></pre>';
}

// Enables use of URL hash to link to individual tabs in the interface
jQuery(document).ready(function() {
    $( "#tabs" ).tabs({
        activate: function(event, ui) {
            event.preventDefault();
            var id = ui.newPanel.attr('id');
        history.replaceState(undefined, undefined, '#' + id.substring(1))
        }
    });
    if(window.location.hash) {
        $('#tabs').tabs({active: $('#tabs a[href="#_' + window.location.hash.substring(1) + '"]').parent().index()});
    }
    $(window).on('hashchange', function() {
        $('#tabs').tabs({active: $('#tabs a[href="#_' + window.location.hash.substring(1) + '"]').parent().index()});
    });
});
