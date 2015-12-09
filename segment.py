from sys import argv
import string

def get_segmentations(sentence):
    title, segment_text = sentence[6].split("=")
    assert title == "#SEGMENT", "Sentence doesn't have expected #SEGMENT line: %s" % sentence
    root = get_ind(filter(is_root, sentence[12:])[0])
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
    sentence += "\n".join(lines[1:6])
    sentence += "#SEGMENT=\n"
    for metaline in lines[7:11]:
        title, content = metaline.split("=")
        sentence += title + "="
        if content:
            kept_things = []
            for thing in content.split(","):
                index = int(thing.strip().split(" ")[0])
                if index >= start and index <= end:
                    kept_things.append(thing)
            sentence += ",".join(kept_things)
        sentence += "\n"
    sentence += lines[11]
    for line in lines[12:]:
        if get_ind(line) >= start and get_ind(line) <= end:
            if get_ind(line) == root:
                parts = line.split("\t")
                sentence += "\t".join(parts[0:4]) + "0\troot" + "\t".join(parts[6:]) + "\n"
            else:
                sentence += line + "\n"
    return sentence

def fix_ends(segs, last):
    new = []
    for i in range(len(segs[:-1])):
        new.append((segs[i][0], segs[i][1], segs[i+1][0]-1))
    new.append((segs[-1][0], segs[-1][1], last))
    return new

if __name__ == "__main__":
    if len(argv) < 3:
        ofn = raw_input("Enter original file name: ")
        cfn = raw_input("Enter corrected file name: ")
    else:
        ofn = argv[1]
        cfn = argv[2]
    o = open(ofn, 'r')
    c = open(cfn, 'r')
    o_sentences = filter(lambda s: s.strip() != "", "".join(o.readlines()).split("\n\n"))
    c_sentences = filter(lambda s: s.strip() != "", "".join(c.readlines()).split("\n\n"))
    new_o = ''
    new_c = ''
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
        oseg = get_segmentations(olines)
        cseg = get_segmentations(clines)
        if len(oseg) == 1 or len(cseg) == 1:
            new_o += o + "\n\n"
            new_c += c + "\n\n"
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
                print "Sentence %s will have to be segmented manually!" % olines[0]
                print list(enumerate(oseg)), "\n", list(enumerate(cseg))
                i = raw_input("Which match (e.g. '0 0')? ")
                while i != "":
                    seg_in_o, seg_in_c = i.split(" ")
                    new_oseg.append(oseg[int(seg_in_o)])
                    new_cseg.append(cseg[int(seg_in_c)])
                    i = raw_input("What else (blank to finish)? ")
                oseg = new_oseg
                cseg = new_cseg
                print oseg
                print cseg
                #new_o += o + "\n\n"
                #new_c += c + "\n\n"
                #continue
        if len(oseg) == 1 or len(cseg) == 1:
            new_o += o + "\n\n"
            new_c += c + "\n\n"
            continue
        oseg = fix_ends(oseg, get_ind(olines[-1]))
        cseg = fix_ends(cseg, get_ind(clines[-1]))
        for suffix, seg in zip(string.ascii_lowercase, oseg):
            #print seg
            new_o += segment(olines, seg[0], seg[1], seg[2], suffix) + "\n"
        for suffix, seg in zip(string.ascii_lowercase, cseg):
            new_c += segment(clines, seg[0], seg[1], seg[2], suffix) + "\n"
    open(ofn+".segmented",'w').write(new_o)
    open(cfn+".segmented",'w').write(new_c)

