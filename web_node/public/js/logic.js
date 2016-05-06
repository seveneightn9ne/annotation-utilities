
/*var error_names = {
	"AGN":"Agreement noun",
	"AGV":"Agreement verb",
	"AGA":"Agreement pronoun",
	"AGD":"Agreement determiner",
	"AGQ":"Agreement quantifier",
	"AS":"Argument structure",
	"CL":"Collocation",
	"CE":"Compound",
	"CD":"Countability determiner",
	"CN":"Countability noun",  
	"CQ":"Countability quantifier",
	"DJ":"Derivation adjective",
	"DY":"Derivation adverb",
	"DD":"Derivation determiner",
	"DN":"Derivation noun",
	"DT":"Derivation preposition",
	"DA":"Derivation pronoun",
	"DQ":"Derivation quantifier",
	"DV":"Derivation verb",
	"FJ":"Form adjective",
	"FY":"Form adverb",
	"FD":"Form determiner",
	"FN":"Form noun",
	"FA":"Form pronoun",
	"FQ":"Form quantifier",
	"FV":"Form verb",
	"IJ":"Formation adjective",
	"IY":"Formation adverb",
	"ID":"Formation determiner",
	"X":"Formation negation",
	"IN":"Formation noun",
	"IA":"Formation pronoun",
	"IQ":"Formation quantifier",
	"IV":"Formation verb",  
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
	"TV":"Tense verb",
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
};*/


$(function() {
	$( document ).tooltip({
		//tooltipClass: "error_tooltip"
	});
});

/*$(".error_tooltip").text(function () {
	return $(this).text().replace("RV", "hello everyone"); 
});*/

/*$(document).ready(function() {
    $('.tooltip').tooltipster();
});*/

function do_search(event) {
	$('#results').empty();
	var query = document.getElementById("search_field").value;
	var error = document.getElementById("error").value;
	var language = document.getElementById("language").value;
	var corpus = document.getElementById("corpus_list").value;
	var show_corr = document.getElementById("corr").checked && corpus=="esl";
	var hl_err = document.getElementById("hl_err").checked;
	$('#results').append("<p>Searching for <b>"+query+"</b>...</p>");	
	var ajax_url = "/search?query="+encodeURIComponent(query)+"&corpus="+corpus+"&error="+error+"&language="+language;
	$.get(ajax_url, success=function(response){
		$('#results').empty();
		$('#results').append(format_response(response, show_corr, hl_err));
		$(".error").addClass("tooltip");
		//$('.tooltip').tooltipster();
		format_errors();
		Annodoc.activate(Config.bratCollData, documentCollections);
	});
}

function update_filter_visibility(value) {
	if(value == "esl") {
		$("#filters").css("display", "inline");
	} else {
		$("#filters").css("display", "none");
	}
}

function format_errors() {
	/*
	var error_corr = $(".err-corr");

	error_corr.each(function(index) {
		var siblings = $(this).siblings();
		console.log($(this).text());
		siblings.each(function(index) {
			//console.log("has sibling "+$(this).text());
		});
		if(siblings.length == 0) {
			console.log($(this).text()+" has 0 siblings");
			$(this).append('<span class="err-orig">HELLO</span>');
		}
	});
	//$( "li.third-item" ).siblings().css( "background-color", "red" );*/
}


function checkSubmit(e) {
		if(e && e.keyCode == 13) {
			document.getElementById("search_button").click();
		}
}

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

function percentify(number_dict) {
	var total = sum_dict(number_dict);
	var percentified_dict = {};
	for (var item in number_dict) {
		percentified_dict[item] = (Math.round(number_dict[item]/total*1000)/10);
	}
	return percentified_dict;
}

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

function sum_dict(my_dict) {
	var total = 0;
	for (var item in my_dict) {
		total += my_dict[item];
	}
	return total;
}

function sentence_text(sentence, match_indices, hl_err) {
	html_string = "";
	if(hl_err) {
		if(sentence.sent_xml != undefined) {
			html_string += sentence.sent_xml;
		} else {
			html_string += sentence.word_sentence;
		}
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

function format_response(response, show_corr, hl_err) {
	var max_results = 10000;
	var html_string = "";
	var corpus_names = {esl:"ESL", eng:"English"};
                
	html_string += "<p><b>"+response.matches.length+"</b> matching sentences for <em>"+response.query.query+"</em> in the "+corpus_names[response.query.corpus]+" corpus.</p>";
	
	//if(response.stats.length > 0) {
		html_string += '<div id="stats">';
		html_string += format_stats_section(response.stats);
		html_string += "</div>";
	//}

	for(var i=0; i<Math.min(response.matches.length, max_results); i++) {
		html_string += '<div class="result">';
		var match_positions = [].concat.apply([], response.matches[i].positions);

		var match_indices = [];
		for(var x=0; x<match_positions.length; x++) {
			match_indices.push(match_positions[x].index);
		}
		
		html_string += '<span class="sent-orig">';
		html_string += sentence_text(response.matches[i].sentence, match_indices, hl_err);
		html_string += '</span>';

		var tree_highlights = ["# sentence-label "+(i+1)+" original"];
		for(var j=0; j<match_positions.length; j++) {
			if(match_positions[j].what == "word") {
				tree_highlights.push('# visual-style '+(match_positions[j].index+1)+' bgColor:#fff59d');
			} else if(match_positions[j].what == "pos") {
				tree_highlights.push('# visual-style '+(match_positions[j].index+1)+' bgColor:#fff59d');
			} else if(match_positions[j].what == "rel") {
				tree_highlights.push('# visual-style '+(response.matches[i].sentence.words[match_positions[j].index].h_ind)+' '+(match_positions[j].index+1)+' '+response.matches[i].sentence.words[match_positions[j].index].rel+' color:#D1C113');
			}
		}
		html_string += wrap_sentence_fulltext(tree_highlights.join("\n")+response.matches[i].sentence.fulltext);
		if(show_corr) {

			html_string += '<span class="sent-corr">';
			html_string += sentence_text(response.matches[i].sentence, match_indices,hl_err);
			html_string += '</span>';

			html_string += wrap_sentence_fulltext("# sentence-label "+(i+1)+" corrected"+response.matches[i].sentence.corrected.fulltext);
		}
		html_string += '</div>';
	}
	return html_string;
}

function wrap_sentence_fulltext(text) {
	return '<pre><code class="language-conllu">'+text+'\n\n</code></pre>';
}


jQuery(document).ready(function() {

	//$('.tooltip').tooltipster();

	console.log($('#search').siblings());

    jQuery('.tabs .tab-links a').on('click', function(e)  {
        var currentAttrValue = jQuery(this).attr('href');
 
        // Show/Hide Tabs
        var activateTab = jQuery(currentAttrValue);
        activateTab.show();
        var tabsToHide = activateTab.siblings();
        tabsToHide.hide();
 
        // Change/remove current tab to active
        jQuery(this).parent('li').addClass('active').siblings().removeClass('active');
 
        e.preventDefault();
    });
});
