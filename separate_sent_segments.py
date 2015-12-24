for version in ('original', 'corrected'):
    output = ''
    take = False
    f = open('treebank.' + version + '.edits.segmented')
    out = open('treebank.' + version + '.segmented-sentences', 'w')
    for line in f:
        if line.startswith("#ID=") and line.strip().endswith(('a','b','c','d','e')):
            idd = line.split("=")[1].strip()
            out.write(idd + "\n")
            take = True
        if take and line.startswith("#SENT"):
            sentence = "=".join(line.split("=")[1:]).strip()
            out.write(sentence + "\n")
            if line.startswith("#SENT="):
                take = False

