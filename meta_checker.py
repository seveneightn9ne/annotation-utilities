from sys import argv

def sanity_checks(numbered_lines, corrected, final):
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
        if line.startswith('#SEGMENT='):
            segs = []
            segments = filter(None,line.split('=')[1].split(','))
            if len(segments) > 0:
                for i in segments:
                    try:
                        a = i.strip().split(' ')
                        ind = int(a[0])
                        rootind = int(a[1])
                    except (ValueError, IndexError):
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
                    segs.append(entry)
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
                if corrected:
                    print ("TYPO on line %d not allowed in corrected sentence" % num)
                a = [x.strip().split(' ') for x in typos]
                for x in a:
                    try:
                        ind = x[0]
                        hind = x[3]
                        map(lambda x: (int(ind),int(hind)), a)
                    except (ValueError, IndexError):
                        typos = []
                        print ("ParseError on line %d: "
                                "incorrect #TYPO format" % num)
                        break
                    if (x[1] not in all_upos or x[2] not in all_pos or
                            x[4] not in all_rel):
                        typos = []
                        print ("ParseError on line %d: "
                                "incorrect #TYPO format" % num)
                        break
            continue
        elif line.startswith('#CONVENTIONS='):
            print ("ParseError on line %d: #CONVENTIONS is outdated." % num)
            continue
            #expletives = []
            #if 'PPDET=' in line:
            #    print ("ParseError on line %d: "
            #            "PPDET is outdated. Please remove." % num)
            #if 'EXPLETIVE=' in line:
            #    expletives = line.split('=',1)[1].split('=')[1].split(',')
            #    if len(expletives) > 0:
            #        try:
            #            map(int, expletives)
            #        except ValueError:
            #            expletives = []
            #            print ("ParseError on line %d: "
            #                    "incorrect #CONVENTIONS format" % num)
            #continue
        elif line.startswith("#EXPLETIVE="):
            expletives = line.split('=')[1].split(',')
            if expletives[0]:
                try:
                    map(int, expletives)
                except ValueError:
                    expletives = []
                    print ("ParseError on line %d: Non numerical EXPLETIVE index" % num)
            else:
                expletives = []
            continue
        elif line.startswith("#MHEAD="):
            mhead_oi = 1
            content = line.split("=")[1]
            if content:
                if corrected:
                    print "ParseError on line %d: MHEAD in corrected sentence" % num
                mheads = content.split(",")
                for mhead in mheads:
                    if mhead:
                        smhead = mhead.split(" ")
                        if not len(smhead) == 3:
                            print "ParseError on line %d: Wrong # arguments to MHEAD" % num
                            continue
                        oi, ci, rel = smhead
                        try:
                            mhead_oi = int(oi)
                            int(ci)
                        except ValueError:
                            print "ParseError on line %d: Non numerical MHEAD index" % num
                        if not rel in all_rels:
                            print "ParseError on line %d: Bad relation %s" % (num, rel)
            continue
        if final and not line:
            if len(current_sentence) > 0:
                for thing in expletives:
                    lnum,l = current_sentence[thing]
                    if (l[1] != 'PRON' or l[2] != 'PRP' or l[4] != 'expl'):
                        print ("SentenceError on line %d: "
                                "incorrectly-annotated expletive" % lnum)
                for ind in segs:
                    lnum,l = current_sentence[ind[1]]
                    nrange = range(int(ind[0]),len(current_sentence)+1)
                    if l[4] != 'parataxis':
                        print ("SentenceError on line %d: "
                                "incorrectly-annotated segment root" % lnum)
                    for num in nrange:
                        jnum,j = current_sentence[str(num)]
                        if j[1] == 'PUNCT'and int(j[3]) not in nrange:
                            print ("SentenceError on line %d: incorrect "
                                    "punctuation hind for segment" % jnum)
                for typo in typos:
                    ind, upos, pos, hind, rel = typo.split(" ")
                    lnum, l = current_sentence[int(ind)]
                    if l[1] == upos or l[2] == pos:
                        print "SentenceError on line %d: TYPO with same annotation" % lnum
            current_sentence = {}
            continue
        if corrected and line.startswith("#SENT="):
            words = line.split("=")[1].split(" ")
            if len(words) >= 3 and words[0].lower() == words[2].lower() and words[1] == ',':
                print "CorrectionError on line %d: Possibly bad correction" % num
            continue
        if line.startswith('#ID=') or line.startswith("#ERR") or line.startswith("#SENT") or line.startswith("#IND\t"):
            continue
        if line.startswith("#"):
            print "Warning on line %d: Unrecognized meta row: %s" % (num, line)
        split_line = line.split('\t')
        current_sentence[split_line[0]] = [num,split_line[1:]]

if __name__ == "__main__":
    if len(argv) < 2:
        fn = raw_input("Enter file name: ")
    else:
        fn = argv[1]
    corrected = (len(argv) > 2 and argv[2] == "--corrected") or (len(argv) > 3 and argv[3] == "--corrected")
    final = (len(argv) > 2 and argv[2] == "--final") or (len(argv) > 3 and argv[3] == "--final")
    print "Corrected =", corrected
    print "Final =", final
    f = open(fn,'r')
    numbered_lines = enumerate(f.read().split('\n'))
    sanity_checks(numbered_lines, corrected, final)
