from sys import argv

def format_check(numbered_lines):
    all_pos = set(["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD",
                    "NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR",
                    "RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP",
                    "VBZ","WDT","WP","WP$","WRB","PUNCT","GW","AFX","ADD","XX"])
    all_upos = set(["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ",
                    "DET","NUM","PART","PRON","SCONJ","PUNCT","SYM","X"])
    all_rel = set(["nsubj","nsubjpass","dobj","iobj","csubj","csubjpass",
                    "ccomp","xcomp","nummod","appos","nmod","nmod:npmod",
                    "nmod:tmod","nmod:poss","acl","acl:relcl","amod","det",
                    "det:predet","neg","case","advcl","advmod","compound",
                    "compound:prt","name","mwe","foreign","goeswith","list",
                    "dislocated","parataxis","remnant","reparandum","vocative",
                    "discourse","expl","aux","auxpass","cop","mark","punct",
                    "conj","cc","root","cc:preconj","dep"])
    for num, line in map(lambda x: (x[0]+1, x[1].strip()), numbered_lines):
        if '#' in line:
            continue
        if not line:
            continue
        line = line.split('\t')
        if len(line) == 7:
            review = line[6].replace('*','0 1').split(' ')
            try:
                map(int,review[4:5]+review[1::2])
            except ValueError or IndexError:
                print "ParseError on line %d: incorrect review format" % num
                continue
            if review[0] not in all_upos or not int(review[0]):
                print "TagError on line %d: unrecognized UPOS tag" % num
            if review[2] not in all_pos or not int(review[2]):
                print "TagError on line %d: unrecognized POS tag" % num
            if review[6] not in all_rel or not int(review[6]):
                print "TagError on line %d: unrecognized REL tag" % num
        elif len(line) > 7:
            print "ParseError on line %d: incorrect review format" % num
            

if __name__ == '__main__':
    if len(argv) < 2:
        fn = raw_input('Enter file name: ')
    else:
        fn = argv[1]
    f = open(fn, 'r')
    numbered_lines = enumerate(f.read().split('\n'))
    format_check(numbered_lines)
