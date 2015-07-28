#!/user/bin/python
import sys

class Sentence(object):
    def __init__(self, numbered_lines):
        self.lines = filter(lambda l: l != None, map(Line.parse_numbered_line,numbered_lines))

    def __str__(self):
        return " ".join(map(lambda line: line.word, self.nlines))

    def validate(self):
        if self.lines != []:
            map(lambda line: line.validate(), self.lines)
            self.validate_projectivity()
            self.validate_hind_in_bounds()

    def validate_hind_in_bounds(self):
        global heads
        found_root = False
        for line in self.lines + filter(lambda l: l != None, [l.correction for l in self.lines]):
            if line.hind > len(self.lines)+1:
                heads += 1
                print "Out of bounds HIND on line %d" % line.lnum
            if line.hind == 0 and line in self.lines: # excludes correction lines from being root
                if found_root:
                    heads += 1
                    print "Multiple root node on line %d" % line.lnum
                found_root = True
        if not found_root:
            heads += 1
            print "No root found in sentence on line %d" % self.lines[0].lnum

    def validate_projectivity(self):
        for line in self.lines:
            global heads
            if line.ind == line.hind:
                heads += 1
                print "Error on line %d: word can not be its own head" % line.lnum
            elif line.ind < line.hind:
                # word comes before its head

                # words between line and its head which have heads before line
                map(lambda l: self.print_projectivity_violation(line, l),
                        filter(lambda l:l.ind > line.ind and l.ind < line.hind and l.hind < line.ind,
                            self.lines))

                #words between line and its head which have heads after line's head
                map(lambda l: self.print_projectivity_violation(line, l),
                        filter(lambda l:l.ind > line.ind and l.ind < line.hind and l.hind > line.hind,
                            self.lines))
            elif line.ind > line.hind:
                # word comes after its head

                # words between line and its head which have heads before line's head
                map(lambda l: self.print_projectivity_violation(line, l),
                        filter(lambda l:l.ind > line.hind and l.ind < line.ind and l.hind < line.hind,
                            self.lines))

                #words between line and its head which have heads after line
                map(lambda l: self.print_projectivity_violation(line, l),
                        filter(lambda l:l.ind > line.hind and l.ind < line.ind and l.hind > line.ind,
                            self.lines))

    def print_projectivity_violation(self, l1, l2):
        global projectivity
        global punctuation
        if l1.upos == "PUNCT" or l2.upos == "PUNCT":
            punctuation += 1
            print "Punctuation-related projectivity violation between lines %d and %d" % (l1.lnum, l2.lnum)
        else:
            projectivity += 1
            print "Projectivity violation between lines %d and %d" % (l1.lnum, l2.lnum)


class Line(object):
    all_pos = set(["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS",
            "PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN",
            "VBP","VBZ","WDT","WP","WP$","WRB","PUNCT","GW","AFX","ADD","XX"])

    all_upos = set(["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ","DET","NUM","PART",
            "PRON","SCONJ","PUNCT","SYM","X"])

    all_rel = set(["nsubj","nsubjpass","dobj","iobj","csubj","csubjpass","ccomp","xcomp","nummod",
            "appos","nmod","nmod:npmod","nmod:tmod","nmod:poss","acl","acl:relcl","amod","det",
            "det:predet","neg","case","advcl","advmod","compound","compound:prt","name",
            "mwe","foreign","goeswith","list","dislocated","parataxis","remnant","reparandum",
            "vocative","discourse","expl","aux","auxpass","cop","mark","punct","conj","cc","root",
            "cc:preconj","dep"])

    def __init__(self, linenum, ind, word, upos, pos, hind, rel, correction=None):
        self.lnum = linenum
        self.ind = ind
        self.word = word
        self.upos = upos
        self.pos = pos
        self.hind = hind
        self.rel = rel
        self.correction = correction

    @staticmethod
    def parse_numbered_line(nline):
        num, sline = nline
        num += 1
        items = sline.split("\t")
        if len(items) < 6:
            print LineParseError(num, "Too few entries", sline)
            return
        #elif len(items) > 6:
            #print LineParseError(num, "Too many entries", sline)
            #return
        try:
            ind = int(items[0])
        except ValueError:
            print LineParseError(num, "Non-numerical line index '%s'" % items[0], sline)
            return
        try:
            hind = int(items[4])
        except ValueError:
            print LineParseError(num, "Non-numerical head index '%s'" % items[4], sline)
            return
        if len(items) == 10: # line contains correction layer
            try:
                c_hind = int(items[8])
            except ValueError:
                print LineParseError(num,
                        "Non-numerical correction head index '%s'" % items[8], sline)
                return
            correction = Line(num, ind, items[1], items[6], items[7], c_hind, items[9])
        else:
            correction = None
        return Line(num, ind, items[1], items[2], items[3], hind, items[5], correction)

    def validate(self):
        self.val_pos_exists()
        self.val_upos_exists()
        self.val_rel_exists()
        if self.correction != None:
            self.correction.validate()

    def val_pos_exists(self):
        global labels
        if not self.pos in self.all_pos:
            labels += 1
            print "Error on line %d: Unrecognized POS tag '%s'" % (self.lnum, self.pos)

    def val_upos_exists(self):
        global labels
        if not self.upos in self.all_upos:
            labels += 1
            print "Error on line %d: Unrecognized UPOS tag '%s'" % (self.lnum, self.upos)

    def val_rel_exists(self):
        global labels
        if not self.rel in self.all_rel:
            labels += 1
            print "Error on line %d: Unrecognized relation '%s'" % (self.lnum, self.rel)


class LineParseError(Exception):
    def __init__(self, lnum, msg, line):
        self.lnum = lnum
        self.msg = msg
        self.line = line

    def __str__(self):
        return "LineParseError on line %d: %s" % (self.lnum, self.msg)


def numbered_lines_to_sentences(numbered_lines,fn):
    f_new = open(fn+'.gen','w')
    sentences = []
    current_sentence = []
    for num, line in map(lambda nline: (nline[0], nline[1].strip()), numbered_lines):
        if line[0:6] == "#SENT=":
            sent_token = line[6:].split(' ')
            token_line = num+1
        if not line:
            if len(current_sentence) > 0:
                #basic checks to make life easier
                current = 1
                token_error = 0
                if len(current_sentence) != len(sent_token):
                    token_error = 1
                    print "TokenError on line %d: number of tokens sent does not match number of entries in sentence!" % (token_line)
                for i in range(len(current_sentence)):
                    listed = current_sentence[i][1].split('\t')
                    if int(listed[0]) != current:   #checks that index is incrementally increasing
                        print LineParseError(current_sentence[i][0]+1, "Missing index", current_sentence[i][1])
                        current += 1
                    current += 1
                    if len(listed) == 6:
                        listed[2] = listed[2].upper()   #fixes casing in UPOS, POS, REL labels
                        listed[3] = listed[3].upper()
                        listed[5] = listed[5].lower()
                    #checks that #SENT matches entries in sentence
                    if sent_token[i].lower() != current_sentence[i][1].split('\t')[1].lower() and not token_error:
                        print "TokenError on line %d: Mismatched token: %s %s" % (current_sentence[i][0]+1, listed[1], sent_token[i])
                        change = raw_input("Would you like to replace the token? y/n : ")
                        if 'y' in change.lower():
                            listed[1] = sent_token[i]
                    current_sentence[i][1] = '\t'.join(listed)
                    f_new.write(current_sentence[i][1]+'\n')    #writes relevant part of line to new file
                f_new.write('\n')
                sentences.append(Sentence(current_sentence))
                current_sentence = []
            continue
        if line[0] == '#':
            f_new.write('\t'.join((line.split('\t')))+'\n') #gets rid of extra tabs and writes to new file
            continue
        if line[0] == '"':
            f_new.write('\t'.join((line.split('\t')))[1:-1]+'\n')   #gets rid of unwanted quotation marks
            continue
        current_sentence.append([num, line])
    return sentences


if __name__ == "__main__":
    global heads
    global labels
    global projectivity
    global punctuation
    heads = 0
    labels = 0
    projectivity = 0
    punctuation = 0
    if len(sys.argv) < 2:
        fn = raw_input("Enter file name: ")
    else:
        fn = sys.argv[1]
    f = open(fn, "r")
    upto = False
    if len(sys.argv) > 2 and sys.argv[2].startswith("--upto="):
        try:
            upto = int(sys.argv[2].split("=")[1])
        except ValueError:
            print "Warning: non-numeric `upto` argument ignored"
    numbered_lines = enumerate(f.read().split("\n"))
    if upto:
        numbered_lines = list(numbered_lines)[:upto]
    sentences = numbered_lines_to_sentences(numbered_lines,fn)
    map(Sentence.validate, sentences)
    print "\nFinal error count:\n" 
    print "strange_hinds: %d \nstrange_labels: %d" % (heads,labels)
    print "projectivity: %d \npunctuation: %d\n" % (projectivity,punctuation)

