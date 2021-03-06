#!/usr/bin/env python
import sys

COLUMNS = ["IND", "WORD", "UPOS", "POS", "HIND", "REL"]

LEGAL_TOKENS = {'POS': ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD",
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

def is_column_value(columnname, value, allow=None):
    """Check if a value is valid for a column."""
    if allow and value in allow:
        return True
    if columnname in LEGAL_TOKENS:
        return value in LEGAL_TOKENS[columnname]
    else:
        # Make sure it's numeric.
        try:
            return 0 <= int(value)
        except ValueError:
            return False

def check_review_content(review_str, line_num, sent_len, anno_tokens):
    '''prints out messages for tagging issues'''
    review_fields = review_str.replace('*', 'CORRECT NONE').split()
    inds = {'UPOS':0, 'POS':2, 'HIND':4, 'REL':6}
    #check UPOS, POS and REL are legal
    for cat in ['UPOS', 'POS', 'REL']:
        correction = review_fields[inds[cat]]
        if correction != 'CORRECT' and correction not in LEGAL_TOKENS[cat]:
            print "TagError on line", line_num, ": unknown", cat, correction
        errnum = review_fields[inds[cat] + 1]
        if not errnum in ("1","2","NONE"):
            print "ErrorError on line", line_num, ": bad error tag", errnum
    if (review_fields[inds['UPOS']] == anno_tokens[3]) and (review_fields[inds['POS']] == anno_tokens[2]):
        print "TagWarning on line", line_num,":when switching POS and UPOS, change the word annotation directly"
    #check HIND
    hind_correction = review_fields[inds['HIND']]
    if hind_correction != 'CORRECT':
        try:
            correction_ind = int(review_fields[inds['HIND']])
            if correction_ind < 0 or correction_ind > sent_len:
                print "TagError on line", line_num, ": HIND out of sentence bounds"
            elif correction_ind == int(anno_tokens[0]):
                print "TagError on line", line_num, ": HIND self referencing"
        except ValueError:
            print "TagError on line", line_num, ": HIND needs to be a number"
    #check review differs from annotation
    for cat in inds:
        if review_fields[inds[cat]] == anno_tokens[2:][inds[cat]/2]:
            print "TagError on line", line_num, ":", cat, "has the same value in the annotation"
    #check error categries
    for cat in inds:
        if review_fields[inds[cat]] != 'CORRECT' and review_fields[inds[cat]+1] not in ['1', '2']:
            print "TagError on line", line_num, ":", cat, "category should be 1 (error), 2 (disagreement)"

def check_review_format(review_str, line_num):
    '''returns a message if there is at least one problem, None otherwise'''
    if not (review_str.startswith('#') or review_str.startswith('@')):
        return "FormatError on line "+str(line_num)+" : Review should start with #/@"
    if not(review_str[1:].strip()):
        return "FormatError on line "+str(line_num)+" : No review"
    if review_str[1:] == '* * * *':
        return "FormatError on line "+str(line_num)+" : These must be at least one change in the review"
    review_fields = review_str[1:].replace('*', 'CORRECT NONE').split()
    if len(review_fields) != 8:
        return "FormatError on line "+str(line_num)+" : too many or too few fields"
    if review_str.startswith('# ') or review_str.startswith('@ '):
        return "FormatError on line "+str(line_num)+" : Review must not have space after #/@"

def check_resolution(annotation_parts, review_str, resolution_str, line_num, sent_len):
    """Check the format of a resolution and its related review."""
    # Review parts is every other part after removing the initial '#'.
    review_parts = review_str[1:].replace("*", "CORRECT NONE").split(" ")[::2]
    resolution_parts = resolution_str.split(" ")
    if resolution_str == "+":
        return
    if resolution_str == "-":
        return
    if len(resolution_parts) == 4:
        zipped = zip(COLUMNS[2:], annotation_parts[2:], review_parts, resolution_parts)
        for column, annotation_part, review_part, resolution_part in zipped:
            # Valid entry for column.
            passert(is_column_value(column, resolution_part, allow=["*", "-", "+"]),
                    ("TagError on line "+str(line_num)+
                     ": Invalid resolution value "+resolution_part+" for "+column))
            # Star in resolution must derive from star in review.
            if resolution_part == "*":
                passert(review_part == "CORRECT",
                        "TagError on line "+str(line_num)+": Invalid resolution: star for "+column)
            # Plus or minus in resolution must derive from non-star in review.
            elif resolution_part in ["+", "-"]:
                passert(review_part != "CORRECT",
                        "TagError on line "+str(line_num)+": Invalid resolution: +/- for "+column)
            else:
                # Resolution can't be the same as the review.
                passert(resolution_part != review_part,
                        "TagError on line "+str(line_num)+": Invalid resolution: same as review for "+column)
                # Resolution can't be the same as the original
                passert(resolution_part != annotation_part,
                        "TagError on line "+str(line_num)+": Invalid resolution: same as original for "+column)
        return

    print "FormatError on line "+str(line_num)+" : Invalid resolution."

def passert(condition, message):
    """Print if the assertion condition fails."""
    if not condition:
        print message

def check_file(path, upto):
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
            #remove ambiguities from the end
            if line_fields[-1].startswith('?'):
                line_fields = line_fields[:-1]
            #line with no reviews
            if len(line_fields) == len(COLUMNS):
                continue
            #line with one review
            elif len(line_fields) == len(COLUMNS) + 1:
                #print "Missing resolution on line %d" % line_num
                review_str = line.split('\t')[-1]
                formatting_issues = check_review_format(review_str, line_num)
                if formatting_issues:
                    print formatting_issues
                else:
                    check_review_content(review_str[1:], line_num, sent_len, line_fields[:len(COLUMNS)])
            #line with a review and resolution
            elif len(line_fields) == len(COLUMNS) + 2:
                annotation_parts = line_fields[:len(COLUMNS)]
                review_str = line_fields[-2]
                formatting_issues = check_review_format(review_str, line_num)
                if formatting_issues:
                    print formatting_issues
                else:
                    check_review_content(review_str[1:], line_num, sent_len, line_fields[:len(COLUMNS)])

                resolution_str = line_fields[-1]
                check_resolution(annotation_parts, review_str, resolution_str, line_num, sent_len)
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
    check_file(fn, upto = upto)
