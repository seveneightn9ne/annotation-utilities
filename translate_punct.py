f = open("treebank.corrected.edits")
o = open("treebank.corrected.edits.punct", "w")

translate = {
        ".": ".",
        "!": ".",
        "!!":".",
        "?":".",
        "??":".",
        "!?":".",
        "?!":".",
        "?!!!":".",
        "!!!!":".",
        ",":",",
        "...":",",
        "....":",",
        "(":"-LRB-",
        "[":"-LRB-",
        "<":"-LRB-",
        "<<":"-LRB-",
        ")":"-RRB-",
        "]":"-RRB-",
        ">":"-RRB-",
        ">>":"-RRB-",
        "$":"$",
        "%":"NN",
        ";":",",
        ":":":",
        "*":"NFP",
        "|":"NFP",
        "~":"NFP",
        "_":"NFP",
        ":)":"NFP",
        "+":"SYM",
        "=":"SYM",
        "-":"HYPH",
        "--":"HYPH"
        }
lines = [""] + f.readlines()
seen_first_quote = False
seen_second_quote = False
for line_num, line in enumerate(lines):
    if line_num == 0:
        continue
    if "PUNCT\tPUNCT" in line:
        sym = line.split("\t")[1]
        try:
            new = translate[sym]
            if new == ',' and lines[line_num+1].strip() == "":
                new = "."
            o.write("\t".join(line.split("\t")[:3]) + "\t" + new + "\t" + "\t".join(line.split("\t")[4:]))
        except KeyError:
            if sym in ["'", "''", "\""]:
                if sym == "'" and not seen_first_quote and int(line.split("\t")[4]) + 1 == int(line.split("\t")[0]):
                    new = "''"
                elif seen_first_quote:
                    new = "''"
                    seen_second_quote = True
                else:
                    new = "``"
                    seen_first_quote = True
                o.write("\t".join(line.split("\t")[:3]) + "\t" + new + "\t" + "\t".join(line.split("\t")[4:]))
            else:
                print "Unknown PUNCT on line %d: %s" % (line_num, sym)
                o.write(line)
    elif line.strip() == "":
        if seen_first_quote and not seen_second_quote:
            print "Sentence with unpaired quotes ending on line %d" % line_num
        seen_first_quote = False
        seen_second_quote = False
        o.write(line)
    else:
        o.write(line)
