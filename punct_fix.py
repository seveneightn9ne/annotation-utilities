#!/usr/bin/python
"""
Takes a .conllu file as argument
Outputs a new file, with suffix .fixed-punct
"""

import sys

lrb = ['``', '-LRB-']
rrb = ['\'\'', '-RRB']

def satisfies_projectivity(ind, hind, sentence):
    """ Is this relation of ind/hind ok? """
    lb_ind = min(hind, ind) # lower-bound index
    ub_ind = max(hind, ind) # upper-bound index
    for line in sentence:
        if line.startswith("#"):
            continue
        line_ind = int(line.split("\t")[0])
        line_hind = int(line.split("\t")[6])
        if line_ind == ind or line_ind == hind:
            continue
        if line_ind < lb_ind or line_ind > ub_ind: # before or after both
            if line_hind > lb_ind and line_hind < ub_ind: # hind is between lb & ub
                error = "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                return (error, False)
        elif line_ind < ub_ind: # in between
            if line_hind < lb_ind or line_hind > ub_ind: # hind is outside both
                error = "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                return (error, False)
        else:
            raise Exception("impossible state")
    return ("", True)

def best_hind_at(i, sentence, limit_i=None):
    """ return the highest possible hind for sentence[i] """
    punct_index = int(sentence[i].split("\t")[0])
    potential_hind = set([])
    offset = i - punct_index # what is the difference between indexes
    root_ind = None # index of the line whose head is root
    #if limit_i != None:
    #    print "\n".join(sentence)
    #print "\tAt index", punct_index
    for j,line in enumerate(sentence):
        if line.startswith("#"):
            continue
        line_index = int(line.split("\t")[0])
        hind = int(line.split("\t")[6])

        rel = line.split("\t")[7]
        #print "considered line=" + str(line_index) + ", hind=" + str(hind) + " for punct at " + str(punct_index)

        if hind == 0:
            root_ind = line_index
            potential_hind.add(root_ind)
        elif ((line_index < punct_index and hind > punct_index)
                or (line_index > punct_index and hind < punct_index)):
            # This line's hind arrow crosses over punct
            potential_hind.add(hind)
            #print "\t", line_index, "<-", hind, "crosses", punct_index
            if limit_i != None and rel != "punct":
                potential_hind.add(line_index)
        elif limit_i != None and line_index + offset in limit_i and hind + offset not in limit_i and rel != "punct":
            #print "\t", line_index, "points out of the segment"
            potential_hind.add(line_index)
    if len(potential_hind) == 1:
        #print "\tonly potential_hind is", potential_hind
        return potential_hind.pop()
    errors = ""
    # There are multiple possible hinds. Only one should satisfy projectivity.
    valid_hinds = set([])
    errors += "\tThought that " + str(potential_hind) + " might be good\n"
    #if limit_i != None:
    #    print errors,
    for hind in potential_hind:
        if limit_i != None and hind + offset not in limit_i:
            errors += "\t" + str(hind) + " + " + str(offset) + " not good because range is limited to " + str(limit_i) + "\n"
            #print error,
            continue
        if hind == punct_index:
            continue
        error, valid = satisfies_projectivity(punct_index, hind, sentence)
        if valid:
            valid_hinds.add(hind)
        else:
            errors += error
    #print errors,
    if len(valid_hinds) != 1:
        #raise Exception("Valid hinds: " + str(valid_hinds) + " for punct:\n" + sentence[i] +
        #        "\nin sentence:\n" + "\n".join(sentence))
        print "MANUALLY CHECK SENTENCE " + sentence[0]
        print errors,
        return int(sentence[i].split("\t")[6]) # return existing notation
    return valid_hinds.pop()

def process_sentences(sentences):
    for sentence in sentences:
        in_lrb = False
        lrb_i = None
        lrb_type = None
        lrb_ranges = {} # key = i of an LRB or RRB, value = range of indices inside them
        for i,line in enumerate(sentence): # Find pairs of LRB/RRB, put in lrb_ranges
            if line.startswith("#") or line.strip() == "":
                continue
            pos = line.split("\t")[4]
            if not in_lrb and pos in lrb:
                in_lrb = True
                lrb_i = i
                lrb_type = lrb.index(pos)
            elif in_lrb and pos in rrb and rrb.index(pos) == lrb_type:
                in_lrb = False
                r = range(lrb_i + 1, i)
                lrb_ranges[lrb_i] = r
                lrb_ranges[i] = r
        for i,line in enumerate(sentence): # Fix LRB/RRB hinds
            if line.startswith("#") or line.strip() == "" or i not in lrb_ranges:
                continue
            pre_hind = "\t".join(line.split("\t")[:6]) + "\t"
            post_hind = "\t" + "\t".join(line.split("\t")[7:])
            new_hind = best_hind_at(i, sentence, lrb_ranges[i])
            sentence[i] = pre_hind + str(new_hind) + post_hind
        for i,line in enumerate(sentence): # Fix all other hinds
            if line.startswith("#") or line.strip() == "" or i in lrb_ranges:
                continue
            if line.split("\t")[7] == "punct":
                pre_hind = "\t".join(line.split("\t")[:6]) + "\t"
                post_hind = "\t" + "\t".join(line.split("\t")[7:])
                new_hind = best_hind_at(i, sentence, lrb_ranges.get(i, None))
                sentence[i] = pre_hind + str(new_hind) + post_hind
    return sentences

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "required arg: .conllu file"
        sys.exit()
    f = open(sys.argv[1], "r")
    sentences = [sent.split("\n") for sent in f.read().split("\n\n")]
    f.close()

    processed = process_sentences(sentences)

    output = "\n".join(["\n".join(sent) + "\n" for sent in sentences])[:-1]
    o = open(sys.argv[1] + ".fixed-punct", "w")
    o.write(output)
    o.close()
