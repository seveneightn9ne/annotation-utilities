# Annotation Utilities for Universal Dependency tagging
## anno_checker.py
Validates an annotation file where the lines are:
```
index    word    universal-pos    ptb-pos    head-index    relation
```
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
* Point out likely mistakes (for example tagging something as `NOUN` and `VB`)
