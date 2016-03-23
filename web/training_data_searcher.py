#!/user/bin/python
import sys, re

match_header = '<pre><code class="language-conllu">'

match_footer = '\n</code></pre>'

punct = [".",",","!","?",":"]

class Sentence(object):
	def __init__(self, lines):
		self.headers = filter(lambda x: x[0]=='#', lines)
		self.errors = []
		lines = filter(lambda x: x[0]!='#', lines)
		self.fulltext = "\n".join(lines)
		self.words = map(Word, lines)
		self.match = None

	def __str__(self):
		return " ".join(self.headers) + " ".join(map(str, self.words))

	def matches(self, string):
		words = string.split(" ")
		for si in range(len(self.words)-len(words)):
			self.match = []
			for (i, word) in enumerate(words):
				word_obj = self.words[si+i]
				if word_obj.matches(word):
					self.match.append(si+i)
				else:
					self.match = None
					break
			if self.match != None:
				return self.match
		return None

	def match_attr(self, attr):
		if self.match == None:
			raise RuntimeError("Querying %s of a nonexistent match" % attr)
		return " ".join(map(lambda w: getattr(w, attr), self.match))


class Word(object):
	all_pos = set(["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS",
			"PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN",
			"VBP","VBZ","WDT","WP","WP$","WRB","PUNCT"])

	all_upos = set(["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ","DET","NUM","PART",
			"PRON","SCONJ","PUNCT","SYM","X"])

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
		self.rel = items[7]

	def __str__(self):
		return self.word

	def matches(self, string):
		if string.isupper() and string != "I":
			return string == self.pos
		if string == self.rel:
			return True
		restring = "^" + string + "$"
		return re.match(restring, self.word, re.I)


def lines_to_sentences(lines):
	sentences = []
	current_sentence = []
	for line in map(lambda line: line.strip(), lines):
		if not line:
			if len(current_sentence) > 0:
				sentences.append(Sentence(current_sentence))
				current_sentence = []
			continue
		current_sentence.append(line)
	return sentences


def analyze_frequency(items, upto=10):
	freqs = {item: items.count(item) for item in set(items)}
	for item in sorted(freqs.keys(), lambda x,y: cmp(freqs[x], freqs[y]), reverse=True)[:upto]:
		#print "%s\t%d" % (item, 100*float(freqs[item])/float(len(items))) + "%"
		pass

def search_corpus(phrase):
	output = []
	corpus = "English.train.conllu"
	f = open(corpus, "r")
	lines = f.read().split("\n")
	sentences = lines_to_sentences(lines)
	sentences = map(lambda s: (s, s.matches(phrase)), sentences)
	matches = filter(lambda s: s[1] is not None, sentences)
	#matches = filter(lambda s: s.matches(phrase), sentences)
	if matches:
		output.append('<div id="search-results-header">')
		output.append("<p>You searched for <i>"+phrase+"</i>.</p>")
		output.append( "<p>"+str(len(matches))+" matching sentences.</p>" )
		output.append('</div>')
		#output.append("Part of Speech:")
		#analyze_frequency(map(lambda m: m.match_attr("pos"), matches))
		#output.append("<p>Relation:")
		#analyze_frequency(map(lambda m: m.match_attr("rel"), matches))
		output.append("")
		for s in matches:
			output.append('<div class="result">')
			sentence = str(s[0]).split(" ")
			build_html_sentence = []
			for i in range(len(sentence)):
				if i>0 and sentence[i] not in punct:
					build_html_sentence.append(" ")
				if i in s[1]:
					build_html_sentence.append('<span class="matched-word">')
					build_html_sentence.append(sentence[i])
					build_html_sentence.append('</span>')
				else:
					build_html_sentence.append(sentence[i])
			output.append("".join(build_html_sentence))
			output.append(match_header)
			for match in s[1]:
				output.append("# visual-style "+str(match+1)+" bgColor:green")

			for line in s[0].fulltext.split("\n"):
				output.append(line)
			output.append(match_footer)
			output.append("</div>")

	else:
		output.append("no matches found")

	return '\n'.join(output)


if __name__ == "__main__" and len(sys.argv) > 1:
	phrase = sys.argv[1].strip("\"")
	#print phrase
	if len(sys.argv) > 2 and sys.argv[2].startswith("--corpus="):
		corpus = sys.argv[2].split("=")[1]
	else:
		corpus = "English.train.conllu"
	f = open(corpus, "r")
	lines = f.read().split("\n")
	sentences = lines_to_sentences(lines)
	matches = filter(lambda s: s.matches(phrase), sentences)
	if matches:
		#print len(matches), "matching sentences.<p>"
		#print "Part of Speech:"
		analyze_frequency(map(lambda m: m.match_attr("pos"), matches))
		#print "<p>Relation:"
		analyze_frequency(map(lambda m: m.match_attr("rel"), matches))
		#print
		for s in matches:
			#print s
			for line in s.fulltext.split("\n"):
				#print line + "<p>"
				pass

	else:
		#print "no matches found"
		pass
