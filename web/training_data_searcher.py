#!/user/bin/python
import sys, re

match_header = '<pre><code class="language-conllu">'

match_footer = '\n</code></pre>'

punct = [".",",","!","?",":"]

RESULTS_LIMIT = 6000

class Sentence(object):
	def __init__(self, lines):
		self.headers = filter(lambda x: x[0]=='#', lines)
		self.errors = []
		for head in self.headers:
			if head.startswith("#SENT"):
				self.errors = re.findall('(?<=ns type=")(.+?)(?=")', head)
			if head.startswith("#ID"):
				self.id = head[4:]
		lines = filter(lambda x: x[0]!='#', lines)
		self.fulltext = "\n".join(lines)
		self.words = map(Word, lines)
		self.match = []

	def __str__(self):
		return " ".join(self.headers) + " ".join(map(str, self.words))

	def setCorrectedVersion(self, corrected):
		self.corrected = corrected

	def sentenceText(self):
		return " ".join(map(str, self.words))

        def triplet_matches(self, string):
                words = string.split()
                if len(words) != 3:
                        return False
                for i, w in enumerate(self.words):
                        hind = w.hind-1
                        if w.matches(words[0]) and w.relmatches(words[1]) and self.words[hind].matches(words[2]):
                                self.match.append([(self.words[i], i), (self.words[hind], hind)])
                return self.match
                
	def matches(self, string, error):
                #search for error type witout query
                if not(string):
                        return error in self.errors
                else:
                        words = string.split()
                        #find query matches
                        search_words = self.words
                        for si in range(len(self.words)-len(words)):
                                matched = True
                                for (i, word) in enumerate(words):
                                        word_obj = self.words[si+i]
                                        if not word_obj.matches(word):
                                                matched = False
                                                break
                                if matched:
                                        myMatch = []
                                        for i in range(len(words)):
                                                myMatch.append((self.words[si+i], si+i))
                                                self.match.append(myMatch)
                        matched_error = not(error.strip()) or error in self.errors
                        if self.match and matched_error:
                                return self.match
                return False

	def match_attr(self, attr):
		if self.match == None:
			raise RuntimeError("Querying %s of a nonexistent match" % attr)
		if len(self.match) == 0:
			return ""
		return " ".join(map(lambda w: getattr(w[0], attr), self.match[0]))


class Word(object):
	all_pos = set(["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS",
			"PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN",
			"VBP","VBZ","WDT","WP","WP$","WRB","PUNCT"])

	all_upos = set(["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ","DET","NUM","PART",
			"PRON","SCONJ","PUNCT","SYM","X"])

	all_errors = set(["AGN","AGV","CL","CN","ID","IV","MA","MD","MT","MV","RA","RD","RJ","RN","RT",
			"RV","RY","UA","UD","UT","UV","TV","AGA","AGD","AGQ","AS","CD","CE","CQ","DA","DD","DV",
			"FD","FJ","FY","W","X","DJ","DN","DY","FN","FV","IJ","IN","IQ","L","MC","MJ","MN","MQ",
			"MY","RC","RQ","UC","UJ","UN","UQ","UY","AG","FQ","DQ","IY","FA","DI","IA","DT","UP","MP",
			"RP","S","SA","SX","M","R","U"])

	all_rel = set(["nsubj","nsubjpass","dobj","iobj","csubj","csubjpass","ccomp","xcomp","nummod",
			"appos","nmod","nmod:npmod","nmod:tmod","nmod:poss","acl","acl:relcl","amod","det",
			"det:predet","neg","case","advcl","advmod","compound","compound:prt","name",
			"mwe","foreign","goeswith","list","dislocated","parataxis","remnant","reparandum",
			"vocative","discourse","expl","aux","auxpass","cop","mark","punct","conj","cc","root",
			"cc:preconj","dep"])

	def __init__(self, line):
		# print "line:", line
		items = line.split("\t")
		self.word = items[1]
		self.pos = items[3]
                self.hind = int(items[6])
		self.rel = items[7]

	def __str__(self):
		return self.word

	def matches(self, string):
		#if string in self.all_errors:
		#	return string == self.word
		if string.isupper() and string != "I":
			return string == self.pos
		if string == self.rel:
			return True
		restring = "^" + string + "$"
		return re.match(restring, self.word, re.I)

        def relmatches(self, string):
		if string == self.rel:
			return True
                return False

def lines_to_sentences(lines, lines_corr=[]):
	
	# create original sentences
	sentences = []
	current_sentence = []
	for line in map(lambda line: line.strip(), lines):
		if not line:
			if len(current_sentence) > 0:
				sentences.append(Sentence(current_sentence))
				current_sentence = []
			continue
		current_sentence.append(line)

	# create corrected sentences
	sentences_corr = {}
	current_corr_sentence = []
	for line_corr in map(lambda line_corr: line_corr.strip(), lines_corr):
		if not line_corr:
			if len(current_corr_sentence) > 0:
				new_corr_sentence = Sentence(current_corr_sentence)
				sentences_corr[new_corr_sentence.id] = new_corr_sentence
				current_corr_sentence = []
			continue
		current_corr_sentence.append(line_corr)

	# match original sentences to corrected sentences
	if len(lines_corr) > 0:
		for sentence in sentences:
			sentence.setCorrectedVersion(sentences_corr[sentence.id])

	return sentences


def analyze_frequency(items, upto=10):
	returnList = []
	freqs = {item: items.count(item) for item in set(items)}
	for item in sorted(freqs.keys(), lambda x,y: cmp(freqs[x], freqs[y]), reverse=True)[:upto]:
		returnList.append("<td>%s</td><td>%d" % (item, 100*float(freqs[item])/float(len(items))) + "%</td>")
	output = []
	output.append('<table>')
	for item in returnList:
		output.append('<tr>')
		output.append(item)
		output.append('</tr>')
	output.append('</table>')
	return "".join(output)

def search_corpus(phrase, triplet_match, error, search_corpus, show_corr):
	output = []
	if search_corpus == "eng":
		corpus = "../data/en-ud-train-1.2.conllu"
		corpus_name = "English"
		f = open(corpus, "r")
		lines = f.read().split("\n")
		lines_corr = []
	else:
		corpus = "../data/en_esl-ud.conllu"
		corpus_corr = "../data/en_cesl-ud.conllu"
		corpus_name = "ESL"
		f = open(corpus, "r")
		f_corr = open(corpus_corr, "r")
		lines = f.read().split("\n")
		lines_corr = f_corr.read().split("\n")
	sentences = lines_to_sentences(lines, lines_corr)
        if triplet_match:
                sentences = map(lambda s: (s, s.triplet_matches(phrase)), sentences)
        else:
                sentences = map(lambda s: (s, s.matches(phrase, error)), sentences)
                
	matches = filter(lambda s: s[1], sentences)
	if len(matches) > RESULTS_LIMIT:
		fullLength = len(matches)
		matches = matches[:RESULTS_LIMIT]
		limited = True
	else:
		limited = False

	#matches = filter(lambda s: s.matches(phrase), sentences)
	if matches:
		output.append('<div id="search-results-header">')
		output.append("<p>You searched for <i>"+phrase+"</i> in the "+corpus_name+" corpus.</p>")
		if (limited):
			output.append( "<p>"+str(fullLength)+" matching sentences. <i>(Results limited to first "+str(RESULTS_LIMIT)+".)</i></p>" )
		else:
			output.append( "<p>"+str(len(matches))+" matching sentences.</p>" )
                output.append('</div>')
                if phrase.split():
                        output.append('<table><tr><td style="vertical-align:top">Part of Speech:')
                        output.append(analyze_frequency(map(lambda m: m[0].match_attr("pos"), matches)))
                        output.append("</td><td>Relation:")
                        output.append(analyze_frequency(map(lambda m: m[0].match_attr("rel"), matches)))
                        output.append("</td></tr></table>")
		for s in matches:
			output.append('<div class="result">')
			sentence = s[0].sentenceText().split(" ")
                        match_indices = []
                        if phrase.strip():
                                match_indices = [x[1] for x in [item for sublist in s[1] for item in sublist]]
			build_html_sentence = []
			for i in range(len(sentence)):
				if i>0 and sentence[i] not in punct:
					build_html_sentence.append(" ")
				if i in match_indices:
					build_html_sentence.append('<span class="matched-word">')
					build_html_sentence.append(sentence[i])
					build_html_sentence.append('</span>')
				else:
					build_html_sentence.append(sentence[i])
			build_html_sentence.append("  ")
			for error in s[0].errors:
				build_html_sentence.append('<span class="error-code">')
				build_html_sentence.append(error)
				build_html_sentence.append('</span>  ')

			output.append("".join(build_html_sentence))
			output.append(match_header)
			for match in match_indices:
				output.append("# visual-style "+str(match+1)+" bgColor:#fff59d")

			for line in s[0].fulltext.split("\n"):
				output.append(line)
			output.append(match_footer)
			output.append("\n")

			if(search_corpus=='esl' and show_corr):
				sentence = s[0].corrected.sentenceText().split(" ")
				build_html_sentence = []
				for i in range(len(sentence)):
					if i>0 and sentence[i] not in punct:
						build_html_sentence.append(" ")
					build_html_sentence.append(sentence[i])
				output.append("".join(build_html_sentence))

				output.append(match_header)
				for line in s[0].corrected.fulltext.split("\n"):
					output.append(line)
				output.append(match_footer)

			output.append("</div>")

	else:
		output.append("no matches found")

	return '\n'.join(output)
