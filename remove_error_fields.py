f = open("treebank.corrected.edits")
o = open("treebank.corrected.edits.noerr", "w")
for line in f:
    if not line.startswith("#ERR"):
        o.write(line)
