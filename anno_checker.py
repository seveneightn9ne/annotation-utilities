#!/user/bin/python
import sys

class Sentence(object):
    def __init__(self, numbered_lines):
        self.lines = filter(lambda l: l != None, map(Line.parse_numbered_line, numbered_lines))

    def __str__(self):
        return " ".join(map(lambda line: line.word, self.nlines))

    def validate(self):
        map(lambda line: line.validate(), self.lines)
        self.validate_projectivity()

    def validate_projectivity(self):
        for line in self.lines:
            if line.ind == line.hind:
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
        print "Projectivity violation between lines %d and %d" % (l1.lnum, l2.lnum)


class Line(object):
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

    def __init__(self, linenum, ind, word, upos, pos, hind, rel):
        self.lnum = linenum
        self.ind = ind
        self.word = word
        self.upos = upos
        self.pos = pos
        self.hind = hind
        self.rel = rel

    @staticmethod
    def parse_numbered_line(nline):
        num, sline = nline
        num += 1
        items = sline.split("\t")
        if len(items) < 6:
            print LineParseError(num, "Too few entries", sline)
            return
        elif len(items) > 6:
            print LineParseError(num, "Too many entries", sline)
            return
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
        return Line(num, ind, items[1], items[2], items[3], hind, items[5])

    def validate(self):
        self.val_pos_exists()
        self.val_upos_exists()
        self.val_rel_exists()

    def val_pos_exists(self):
        if not self.pos in self.all_pos:
            print "Error on line %d: Unrecognized POS tag '%s'" % (self.lnum, self.pos)

    def val_upos_exists(self):
        if not self.upos in self.all_upos:
            print "Error on line %d: Unrecognized UPOS tag '%s'" % (self.lnum, self.upos)

    def val_rel_exists(self):
        if not self.rel in self.all_rel:
            print "Error on line %d: Unrecognized relation '%s'" % (self.lnum, self.rel)


class LineParseError(Exception):
    def __init__(self, lnum, msg, line):
        self.lnum = lnum
        self.msg = msg
        self.line = line

    def __str__(self):
        return "LineParseError on line %d: %s" % (self.lnum, self.msg)


def numbered_lines_to_sentences(numbered_lines):
    sentences = []
    current_sentence = []
    for num, line in map(lambda nline: (nline[0], nline[1].strip()), numbered_lines):
        if not line:
            if len(current_sentence) > 0:
                sentences.append(Sentence(current_sentence))
                current_sentence = []
            continue
        if line[0] == '#':
            continue
        current_sentence.append((num, line))
    return sentences


if __name__ == "__main__":
    if len(sys.argv) < 2:
        fn = raw_input("Enter file name: ")
    else:
        fn = sys.argv[1]
    f = open(fn, "r")
    numbered_lines = enumerate(f.read().split("\n"))
    sentences = numbered_lines_to_sentences(numbered_lines)
    map(Sentence.validate, sentences)


