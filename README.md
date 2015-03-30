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

### Currently checks:
* Correct format of lines (tab separated, 6 items on each line)
* `universal-pos` is in [this list](http://universaldependencies.github.io/docs/en/pos/all.html) of UPOS tags
* `ptb-pos` is in [this list](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html) or `PUNCT`
* `relation` is in [this list](http://universaldependencies.github.io/docs/en/dep/all.html)
* [Projectivity](http://en.wikipedia.org/wiki/Discontinuity_\(linguistics\)) (crossing dependency arrows). 
  Our dependency grammar is based on a model that prefers but does not require projectivity, so sometimes these 
  errors are OK
  
### Future Work:
* Make sure each `head-index` is in the sentence
* Make sure each `index` is sequential starting from 1 (probably unnecessary)
* Point out likely mistakes (for example tagging something as `NOUN` and `VB`)

## training_data_searcher.py
Searches `English.train.connlu` for sentences with a matching phrase
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
