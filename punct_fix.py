#!/usr/bin/python
"""
Takes a .conllu file as argument
Outputs a new file, with suffix .fixed-punct
"""

import sys

def best_hind_at(i, sentence):
    """ return the highest possible hind for sentence[i] """
    punct_index = int(sentence[i].split("\t")[0])
    potential_hind = set([])
    offset = i - punct_index # what is the difference between indexes
    root_ind = None # index of the line whose head is root
    for j,line in enumerate(sentence):
        if line.startswith("#"):
            continue
        line_index = int(line.split("\t")[0])
        hind = int(line.split("\t")[6])
        if hind == 0:
            root_ind = line_index
        if ((line_index < punct_index and hind > punct_index)
                or (line_index > punct_index and hind < punct_index)):
            # This line's hind arrow crosses over punct
            potential_hind.add(hind)

    if root_ind == None:
        raise Exception("Sentence has no root\n" + "\n".join(sentence))
    potential_hind.add(root_ind)
    if len(potential_hind) == 1:
        return potential_hind.pop()
    errors = ""
    # There are multiple possible hinds. Only one should satisfy projectivity.
    valid_hinds = set([])
    errors += "\tThought that " + str(potential_hind) + " might be good\n"
    for hind in potential_hind:
        if hind < punct_index:
            valid = True
            for line in sentence:
                if line.startswith("#"):
                    continue
                line_ind = int(line.split("\t")[0])
                line_hind = int(line.split("\t")[6])
                if line_ind == punct_index or line_ind == hind:
                    continue
                if line_ind < hind or line_ind > punct_index: # before or after both
                    if line_hind > hind and line_hind < punct_index:
                        errors += "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                        valid = False
                        break
                elif line_ind < punct_index: # in between
                    if line_hind < hind or line_hind > punct_index:
                        errors += "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                        valid = False
                        break
                else:
                    raise Exception("impossible state")
            if valid:
                valid_hinds.add(hind)
        elif hind > punct_index: #mostly the same as above, just backwards
            valid = True
            for line in sentence:
                if line.startswith("#"):
                    continue
                line_ind = int(line.split("\t")[0])
                line_hind = int(line.split("\t")[6])
                if line_ind == punct_index or line_ind == hind:
                    continue
                if line_ind < punct_index or line_ind > hind: # before or after both
                    if line_hind > punct_index and line_hind < hind:
                        valid = False
                        errors += "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                        break
                elif line_ind < hind: # in between
                    if line_hind < punct_index or line_hind > hind:
                        valid = False
                        errors += "\t" + str(hind) + " not good because of " + str(line_ind) + "\n"
                        break
                else:
                    raise Exception("impossible state")
            if valid:
                valid_hinds.add(hind)
    if len(valid_hinds) != 1:
        #raise Exception("Valid hinds: " + str(valid_hinds) + " for punct:\n" + sentence[i] +
        #        "\nin sentence:\n" + "\n".join(sentence))
        print "MANUALLY CHECK SENTENCE " + sentence[0]
        print errors,
        return int(sentence[i].split("\t")[6]) # return existing notation
    return valid_hinds.pop()

def process_sentences(sentences):
    for sentence in sentences:
        for i,line in enumerate(sentence):
            if line.startswith("#") or line.strip() == "":
                continue
            if line.split("\t")[7] == "punct":
                pre_hind = "\t".join(line.split("\t")[:6]) + "\t"
                post_hind = "\t" + "\t".join(line.split("\t")[7:])
                sentence[i] = pre_hind + str(best_hind_at(i, sentence)) + post_hind
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
