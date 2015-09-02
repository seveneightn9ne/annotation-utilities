from sys import argv

def sanity_checks(numbered_lines):
    current_sentence = {}
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
    for num, line in map(lambda x: (x[0]+1,x[1].strip()), numbered_lines):
        if line.startswith('#Segment='):
            seg_roots = []
            segments = filter(None,line.split('=')[1].split(','))
            if len(segments) > 0:
                for i in segments:
                    try:
                        a = i.strip().split(' ')
                        ind = int(a[0])
                        rootind = int(a[1])
                    except ValueError or IndexError:
                        segments = []
                        print ("ParseError on line %d: "
                                "incorrect #Segment format" % num)
                        continue
                    entry = i.strip().split(' ')
                    if int(entry[0]) > int(entry[1]) or len(entry)>2:
                        segments = []
                        print ("ParseError on line %d: "
                                "incorrect #Segment format" % num)
                        continue
                    seg_roots.append(entry[1])
            continue
        elif line.startswith('#UNSURE='):
            unsures = filter(None,line.split('=')[1].split(','))
            if len(unsures) > 0:
                try:
                    a = [x.split(' ') for x in unsures]
                    map(lambda x: int(x[0]), a)
                except ValueError:
                    unsures = []
                    print ("ParseError on line %d: "
                            "incorrect #UNSURE format" % num)
            continue
        elif line.startswith('#TYPO='):
            typos = filter(None,line.split('=')[1].split(','))
            if len(typos) > 0:
                a = [x.split(' ') for x in typos]
                try:
                    ind = x[0]
                    hind = x[3]
                    map(lambda x: (int(ind),int(hind)), a)
                except ValueError or IndexError:
                    typos = []
                    print ("ParseError on line %d: "
                            "incorrect #TYPO format" % num)
                    continue
                for i in a:
                    if (i[1] not in all_upos or i[2] not in all_pos or
                            i[4] not in all_rel):
                        typos = []
                        print ("ParseError on line %d: "
                                "incorrect #TYPO format" % num)
            continue
        elif line.startswith('#CONVENTIONS='):
            expletives = []
            if 'PPDET=' in line:
                print ("ParseError on line %d: "
                        "PPDET is outdated. Please remove." % num)
            if 'EXPLETIVE=' in line:
                expletives = line.split('=',1)[1].split('=')[1].split(',')
                if len(expletives) > 0:
                    try:
                        map(int, expletives)
                    except ValueError:
                        expletives = []
                        print ("ParseError on line %d: "
                                "incorrect #CONVENTIONS format" % num)
            continue
        if not line:
            if len(current_sentence) > 0:
                for thing in expletives:
                    lnum,l = current_sentence[thing]
                    if (l[1] != 'PRON' or l[2] != 'PRP' or l[4] != 'expl'):
                        print ("ParseError on line %d: "
                                "incorrectly-annotated expletive" % lnum)
                for ind in seg_roots:
                    lnum,l = current_sentence[ind]
                    if l[4] != 'parataxis':
                        print ("ParseError on line %d: "
                                "incorrectly-annotated segment root" % lnum)
            current_sentence = {}
            continue
        if line.startswith('#'):
            continue
        split_line = line.split('\t')
        current_sentence[split_line[0]] = [num,split_line[1:]]

if __name__ == "__main__":
    if len(argv) < 2:
        fn = raw_input("Enter file name: ")
    else:
        fn = argv[1]
    f = open(fn,'r')
    numbered_lines = enumerate(f.read().split('\n'))
    sanity_checks(numbered_lines)
