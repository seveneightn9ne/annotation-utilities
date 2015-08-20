import sys

legal_tokens = {'POS': ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD",
                        "NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR",
                        "RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP",
                        "VBZ","WDT","WP","WP$","WRB","PUNCT","GW","AFX","ADD","XX"],
                'UPOS':["ADJ","ADV","INTJ","NOUN","PROPN","VERB","ADP","AUX","CONJ",
                        "DET","NUM","PART","PRON","SCONJ","PUNCT","SYM","X"],
                'REL' :["nsubj","nsubjpass","dobj","iobj","csubj","csubjpass",
                        "ccomp","xcomp","nummod","appos","nmod","nmod:npmod",
                        "nmod:tmod","nmod:poss","acl","acl:relcl","amod","det",
                        "det:predet","neg","case","advcl","advmod","compound",
                        "compound:prt","name","mwe","foreign","goeswith","list",
                        "dislocated","parataxis","remnant","reparandum","vocative",
                        "discourse","expl","aux","auxpass","cop","mark","punct",
                        "conj","cc","root","cc:preconj","dep"]}

def check_review_content(review_str, line_num, sent_len, anno_tokens):
    '''prints out messages for tagging issues'''
    review_fields = review_str.replace('*', 'CORRECT NONE').split()
    inds = {'UPOS':0, 'POS':2, 'HIND':4, 'REL':6} 
    #check UPOS, POS and REL are legal
    for cat in ['UPOS', 'POS', 'REL']:
        correction = review_fields[inds[cat]]
        if correction != 'CORRECT' and correction not in legal_tokens[cat]:
            print "TagError on line", line_num, ": unknown", cat, correction 
    #check HIND
    hind_correction = review_fields[inds['HIND']]
    if hind_correction != 'CORRECT':
        try:
            correction_ind = int(review_fields[inds['HIND']])
            if correction_ind < 1 or correction_ind > sent_len:
                print "TagError on line", line_num, ": HIND out of sentence bounds"
            elif correction_ind == line_num:
                print "TagError on line", line_num, ": HIND self referencing"
        except ValueError:
            print "TagError on line", line_num, ": HIND needs to be a number"
    #check review differs from annotation
    for cat in inds:
        if review_fields[inds[cat]] == anno_tokens[inds[cat]/2]:
            print "TagError on line", line_num, ":", cat, "has the same value in the annotation"
    #check error categries
    for cat in inds:
        if review_fields[inds[cat]] != 'CORRECT' and review_fields[inds[cat]+1] not in ['1', '2', '3']:
            print "TagError on line", line_num, ":", cat, "category should be 1 (error), 2 (convention) or 3 (disagreement)" 

def check_review_format(review_str, line_num):
    '''returns a message if there is at least one problem, None otherwise'''
    if not review_str.startswith('#'):
        return "FormatError on line "+str(line_num)+" : Review should start with #"
    if not(review_str[1:].strip()):
        return "FormatError on line "+str(line_num)+" : No review"
    if review_str[1:] == '* * * *':
        return "FormatError on line "+str(line_num)+" : These must be at least one change in the review"
    review_fields = review_str[1:].replace('*', 'CORRECT NONE').split()
    if len(review_fields) != 8:   
        return "FormatError on line "+str(line_num)+" : too many or too few fields"
    
def check_reviews(path, upto):
    line_num = 0
    for sent in open(path).read().split('\n\n'):
        sent_len = sum([1 for l in sent.strip().split('\n') if not(l.startswith('#'))])
        for line in sent.split('\n'):
            line_num += 1
            if upto and line_num > upto:
                return
            line = line.strip()
            #metadata line or empty line
            if (line.startswith('#')) or (not line):
                continue    
            line_fields = line.split('\t')
            #approved line
            if len(line_fields) == 6:
                continue
            #reviewed line
            elif len(line_fields) == 7:
                review_str = line.split('\t')[6]
                formatting_issues = check_review_format(review_str, line_num)
                if formatting_issues:
                    print formatting_issues
                else:
                    check_review_content(review_str[1:], line_num, sent_len, line_fields[2:6])
            #something is wrong with the line
            else:
                print "LineError on line "+str(line_num)+": check line"
        line_num += 1
                        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        fn = raw_input('Enter file name: ')
    else:
        fn = sys.argv[1]
    upto = False
    if len(sys.argv) > 2 and sys.argv[2].startswith("--upto="):
        try:
            upto = int(sys.argv[2].split("=")[1])
        except ValueError:
            print "Warning: non-numeric `upto` argument ignored"
    check_reviews(fn, upto = upto)
