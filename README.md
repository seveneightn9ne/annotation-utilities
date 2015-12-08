# Utilities for Universal Dependency Annotation
## anno_checker.py
Validates an annotation file where the lines are:
```
index    word    universal-pos    ptb-pos    head-index    relation
```
### Usage
```
$ python anno_checker.py my_file.anno
```
It will output each error on a line. If there are parsing errors, you will need to run it again to get the semantic errors. No output means everything is good.

If there is a mismatch between the tokenized sentence in `#SENT` and the entries in the actual sentence, the script will prompt the user as follows:
```
$ TokenError on line <line number>: Mismatched token: <entry in sentence> <entry in #SENT>
Would you like to replace the token? y/n : 
```
Entering `y` or `yes` will replace the entry in the sentence with the corresponding entry in #SENT.

### Currently checks:
* Correct format of lines (tab separated, 6 items on each line, proper capitalization of tags)
* `universal-pos` is in [this list](http://universaldependencies.github.io/docs/en/pos/all.html) of UPOS tags
* `ptb-pos` is in [this list](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html) or `PUNCT`
* `relation` is in [this list](http://universaldependencies.github.io/docs/en/dep/all.html)
* [Projectivity](http://en.wikipedia.org/wiki/Discontinuity_\(linguistics\)) (crossing dependency arrows). 
  Our dependency grammar is based on a model that prefers but does not require projectivity, so sometimes these 
  errors are OK
* `index` is sequential starting from 1 (probably unnecessary)
* `#SENT` and entries of actual sentence are the same
* no trailing tabs in metadata

### Future Work:
* Make sure each `head-index` is in the sentence
* Point out likely mistakes (for example tagging something as `NOUN` and `VB`)

## meta_checker.py
Checks metadata consistency and format correctness for an annotation file where the lines are:
```
index    word    universal-pos    ptb-pos    head-index    relation
```
### Usage
```
$ python meta_checker.py my_file.anno
```
It will output each error on a line. If there are parsing errors, you will need to run it again to get any errors in the actual annotations. No output means everything is good.

### Currently checks:
* Proper formatting for `#Segment`, `#UNSURE`, `#TYPO`, and `#CONVENTIONS` metadata
* For `#Segment`: head is parataxis, proper punctuation hind
* For `#CONVENTIONS`: appropriate tagging for `EXPLETIVE`, reminds user to remove outdated `PPDET` tag

### Future Work:
* More specific and detailed errors

## review_checker.py
Checks that any reviews, marked by `#` in a column to the right of the original annotation, are properly formatted.
Checks that resolutions, if they exist, are properly formatted and refer correctly to the review.

### Usage
```
$ python review_checker.py my_file.review [upto=...]
```
Prints out issues with review formatting and content.
FormatError indicates problems with the format of the review.
TagError indicates problems with specific tags / error categories.

### Currently checks:
* Proper formatting of `#UPOS CAT POS CAT HIND CAT REL CAT`
* `UPOS`, `POS`, and `REL` are all valid tags
* `HIND` is a number, within sentence bounds, and not selfe referencing
* All proposed tags differ from the annotation tags
* `CAT` is a number between 1-3

### Future Work:
* Warnings when you forget to add corrections that you made in the original file to the corrected file.

## resolver.py
Applies resolutions to lines containing an annotation, review, and resolution.

### Usage
```
# Run with --help to see options and usage example.
$ ./resolver.py --help
# Run the resolver on a file with reviews and resolutions.
$ ./resolver.py jess.original
# Some errors reported, but output file written.
> line 1336: ResolveException('Review wrong length',)
> line 2729: ResolveException('conj:preconvalid value for column REL
> Output written to jess.original.resolve.resolved
# Use a diff tool (like meld) to manually verify some of the output.
$ meld jess.original.resolve jess.original.resolve.resolved
```

## training_data_searcher.py
Searches `English.train.conllu` for sentences with a matching phrase
### Usage
```
$ python training_data_searcher.py "search phrase" | less
```
The search phrase can be a combination of regexes that match words, and UPOS tags.

Examples:
* `"go \w+ing"` matches "go fishing", "go shopping", etc.
* `"go VERB"` matches the above, plus "go pull", etc.
* `"DET NOUN NOUN"` "an investment firm", etc.

It outputs each full sentence, so it's recommended to pipe through `less`.
