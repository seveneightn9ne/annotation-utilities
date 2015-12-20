from sys import argv
import string, pprint, re

matches = [
        [(0,0), (1,2), (2,3), (3,4)],
        [(0,0), (1,2)],
        [(0,0), (1,1)],
        [(0,0), (2,1)],
        [(0,0), (1,1), (2,4), (3,6)],
        [(0,0), (1,2)],
        [(0,0), (1,1)]]
matches_i = 0

def get_segmentations(sentence):
    title, segment_text = sentence[6].split("=")
    assert title == "#SEGMENT", "Sentence doesn't have expected #SEGMENT line: %s" % sentence
    try:
        root = get_ind(filter(is_root, sentence[12:])[0])
    except IndexError:
        pprint.pprint(sentence)
        raise RuntimeError("aah")
    segments = [(1,root)]
    if segment_text:
        for segment in segment_text.split(","):
            try:
                ind, rootind = segment.strip().split(" ")
            except ValueError:
                print "Badly formatted #SEGMENT for sentence %s: %s" % (sentence[0], segment)
                break
            segments[-1] = (segments[-1][0], segments[-1][1], int(ind)-1)
            segments.append((int(ind), int(rootind)))
    segments[-1] = (segments[-1][0], segments[-1][1], get_ind(sentence[-1]))
    #print segments
    return segments

def is_root(line):
    return line.split("\t")[4] == '0'

def get_ind(line):
    return int(line.split("\t")[0])

def segment(lines, start, root, end, idsuffix):
    sentence = lines[0] + idsuffix + "\n"
    sentence += "\n".join(lines[1:6]) + "\n"
    sentence += "#SEGMENT=\n"
    for metaline in lines[7:11]:
        title, content = metaline.split("=")
        sentence += title + "="
        if content:
            kept_things = []
            for thing in content.split(","):
                index = int(thing.strip().split(" ")[0])
                if index >= start and index <= end:
                    new_thing = str(index-start + 1)
                    if len(thing.strip().split(" ")) > 1:
                        new_thing += " " + " ".join(thing.strip().split(" ")[1:])
                    kept_things.append(new_thing)
            sentence += ",".join(kept_things)
        sentence += "\n"
    sentence += lines[11] + "\n"
    for line in lines[12:]:
        new_root = str(root-start + 1)
        if get_ind(line) >= start and get_ind(line) <= end:
            parts = shift_line_indices(line,start-1,new_root).split("\t")
            dupe_review = re.compile('[@#]\* \* ' + parts[4] + ' [123] \*')
            dupe_root_review = re.compile('[@#]((\*)|(.+ [123])) ((\*)|(.+ [123])) ((((\d+ [123])|(\*)) parataxis [123])|(\d+ [123] \*))')
            no_kept_root_review = re.compile('[@#]\* \*')
            if get_ind(line) == root:
                if len(parts)>6 and parts[7] == "+" and dupe_root_review.match(parts[6]):
                    if no_kept_root_review.match(parts[6]):
                        sentence += "\t".join(parts[0:4]) + "\t0\troot\n"
                    else:
                        sentence += "\t".join(parts[0:4]) + "\t0\troot\t" + \
                            " ".join(parts[6].replace("*","* *").split(" ")[:4]).replace("* *", "*") + " * *\t+\n"
                else:
                    sentence += ("\t".join(parts[0:4]) + "\t0\troot\t" + "\t".join(parts[6:])).strip() + "\n"
            elif len(parts) > 6 and parts[7] == "+" and dupe_review.match(parts[6]):
                sentence += "\t".join(parts[:6]) + "\n"
            else:
                sentence += "\t".join(parts) + "\n"
    return sentence

def shift_line_indices(line, shift, new_root):
    bits = line.split("\t")
    bits[0] = shift_index(bits[0],shift, new_root)
    bits[4] = shift_index(bits[4],shift, new_root)
    if len(bits) >= 7: #review
        review = bits[6].replace("*","* *").split(" ")
        review[4] = shift_index(review[4],shift, new_root) if review[4] != "*" else "*"
        bits[6] = " ".join(review).replace("* *","*")
    if len(bits) >= 8: #resolution
        if len(bits[7].split(" ")) > 1: #broken out
            res = bits[7].split(" ")
            res[2] = shift_index(res[2],shift,new_root) if res[2] not in "+-*" else res[2]
            bits[7] = " ".join(res)
    return "\t".join(bits)

def shift_index(index,shift,new_root):
    if index == "0":
        return "0"
    if int(index) - shift <= 0:
        return new_root
    return str(int(index) - shift)


def fix_ends(segs, last):
    new = []
    for i in range(len(segs[:-1])):
        new.append((segs[i][0], segs[i][1], segs[i+1][0]-1))
    new.append((segs[-1][0], segs[-1][1], last))
    return new

if __name__ == "__main__":
    if len(argv) < 4:
        ofn = raw_input("Enter original file name: ")
        cfn = raw_input("Enter corrected file name: ")
        mfn = raw_input("Enter meta-index file name: ")
    else:
        ofn = argv[1]
        cfn = argv[2]
        mfn = argv[3]
    o = open(ofn, 'r')
    c = open(cfn, 'r')
    m = open(mfn, 'r')
    o_sentences = filter(lambda s: s.strip() != "", "".join(o.readlines()).split("\n\n"))
    c_sentences = filter(lambda s: s.strip() != "", "".join(c.readlines()).split("\n\n"))
    meta = {line.split("\t")[0]: "\t".join(line.split("\t")[1:]) for line in m.readlines()}
    new_o = ''
    new_c = ''
    new_m = ''
    assert len(o_sentences) == len(c_sentences), \
            "Number of sentences differ.\n0: %s\n%s\n\nlast:%s%s" % \
            (o_sentences[0], c_sentences[0], o_sentences[-1], c_sentences[-1])
    sentences = zip(o_sentences, c_sentences)
    for o,c in sentences:
        olines = o.split("\n")
        clines = c.split("\n")
        if not olines[0:5] == clines[0:5]:
            print "ParseError on sentence %s: Metadata differs in corrected file" % olines[0]
            #print "\n".join(olines[0:5])
            #print "\n".join(clines[0:5])
            #print "---------------------------------------------------------------------------"
    for o,c in sentences:
        olines = o.split("\n")
        clines = c.split("\n")
        sent_id = olines[0].split("=")[1]
        oseg = get_segmentations(olines)
        cseg = get_segmentations(clines)
        if len(oseg) == 1 or len(cseg) == 1:
            new_o += o + "\n\n"
            new_c += c + "\n\n"
            new_m += sent_id + "\t" + meta[sent_id].strip() + "\n"
            continue
        if len(oseg) != len(cseg):
            #print oseg
            #print cseg
            if len(oseg) < len(cseg):
                try_oseg = oseg
                try_cseg = filter(lambda seg: any([c[0:2] == seg[0:2] for c in oseg]), cseg)
            else:
                try_cseg = cseg
                try_oseg = filter(lambda seg: any([c[0:2] == seg[0:2] for c in cseg]), oseg)
            #print oseg
            #print cseg
            #if len(oseg) == 1:
            #    print "Skipping %s because no matching segments" % olines[0]
            #    #print oseg
            #    #print cseg
            #    new_o += o + "\n\n"
            #    new_c += c + "\n\n"
            #    continue
            if len(try_oseg) == len(try_cseg):
                oseg = try_oseg
                cseg = try_cseg
            else:
                new_oseg = []
                new_cseg = []
                #print "Sentence %s will have to be segmented manually!" % olines[0]
                #print list(enumerate(oseg)), "\n", list(enumerate(cseg))
                #i = raw_input("Which match (e.g. '0 0')? ")
                pairs = matches[matches_i]
                matches_i += 1
                for pair in pairs:
                    new_oseg.append(oseg[pair[0]])
                    new_cseg.append(cseg[pair[1]])
                #while i != "":
                #    seg_in_o, seg_in_c = i.split(" ")
                #    new_oseg.append(oseg[int(seg_in_o)])
                #    new_cseg.append(cseg[int(seg_in_c)])
                #    i = raw_input("What else (blank to finish)? ")
                oseg = new_oseg
                cseg = new_cseg
                #print oseg
                #print cseg
                #new_o += o + "\n\n"
                #new_c += c + "\n\n"
                #continue
        if len(oseg) == 1 or len(cseg) == 1:
            new_o += o + "\n\n"
            new_c += c + "\n\n"
            new_m += sent_id + "\t" + meta[sent_id].strip() + "\n"
            continue
        oseg = fix_ends(oseg, get_ind(olines[-1]))
        cseg = fix_ends(cseg, get_ind(clines[-1]))
        assert len(oseg) == len(cseg)
        for suffix, seg in zip(string.ascii_lowercase, oseg):
            #print seg
            new_o += segment(olines, seg[0], seg[1], seg[2], suffix) + "\n"
            new_m += sent_id + suffix + "\t" + meta[sent_id] + "\n"
        for suffix, seg in zip(string.ascii_lowercase, cseg):
            new_c += segment(clines, seg[0], seg[1], seg[2], suffix) + "\n"
    open(ofn+".segmented",'w').write(new_o)
    open(cfn+".segmented",'w').write(new_c)
    open(mfn+".segmented",'w').write(new_m)

