#!/usr/bin/env python
"""
Tool to apply reviews and resolutions.

Usage:
    ./resolver.py <input-path> <output-path>

Example:
    # Run the resolver on a file with reviews and resolutions.
    $ ./resolver.py jess.original
    # Some errors reported, but output file written.
    > line 1336: ResolveException('Review wrong length',)
    > line 2729: ResolveException('conj:preconj invalid value for column REL
    # Use a diff tool to manually verify some of the output.
    $ meld jess.original.resolve jess.original.resolve.resolved
"""
from docopt import docopt
import traceback

COLUMNS = ["IND", "WORD", "UPOS", "POS", "HIND", "REL"]

LEGAL_TOKENS = {'POS': ["CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD",
                        "NN", "NNS", "NNP", "NNPS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR",
                        "RBS", "RP", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP",
                        "VBZ", "WDT", "WP", "WP$", "WRB", "PUNCT", "GW", "AFX", "ADD", "XX"],
                'UPOS': ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "ADP", "AUX", "CONJ",
                         "DET", "NUM", "PART", "PRON", "SCONJ", "PUNCT", "SYM", "X"],
                'REL': ["nsubj", "nsubjpass", "dobj", "iobj", "csubj", "csubjpass",
                        "ccomp", "xcomp", "nummod", "appos", "nmod", "nmod:npmod",
                        "nmod:tmod", "nmod:poss", "acl", "acl:relcl", "amod", "det",
                        "det:predet", "neg", "case", "advcl", "advmod", "compound",
                        "compound:prt", "name", "mwe", "foreign", "goeswith", "list",
                        "dislocated", "parataxis", "remnant", "reparandum", "vocative",
                        "discourse", "expl", "aux", "auxpass", "cop", "mark", "punct",
                        "conj", "cc", "root", "cc:preconj", "dep"]}


class ResolveException(Exception):
    """Exception when something goes wrong while applying resolution."""
    @staticmethod
    def unless(condition, message=None):
        """Assert using this exception."""
        if not condition:
            raise ResolveException(message)


class ParseException(Exception):
    """Exception when parsing data fails."""
    @staticmethod
    def unless(condition, message=None):
        """Assert using this exception."""
        if not condition:
            raise ResolveException(message)


def is_column_value(columnname, value, allow=None):
    """Check if a value is valid for a column."""
    if allow and value in allow:
        return True
    if columnname in LEGAL_TOKENS:
        return value in LEGAL_TOKENS[columnname]
    else:
        # Make sure it's numeric.
        try:
            return 0 <= int(value)
        except ValueError:
            return False


def assert_column_value(columnname, value, allow=None):
    ResolveException.unless(is_column_value(columnname, value, allow=allow),
                            "{} invalid value for column {}".format(value, columnname))


def resolve(annotation, review, resolution):
    """Apply a resolution.

    The line should be validity checked elsewhere.

    Args:
        annotation: Original annotation. (list of size COLUMNS)
        review: Reviewer notes. (list of size COLUMNS-2)
        resolution: Resolver notes. (list of size COLUMNS-2)
    Returns:
        A list of size COLUMNS of the new line.
    Raises:
        ResolveException: If something goes wrong along the way.
    """
    if resolution == "+" or resolution == ["+"]:
        resolution = ["+"] * (len(COLUMNS) - 2)
    if resolution == "-" or resolution == ["-"]:
        resolution = ["-"] * (len(COLUMNS) - 2)

    final = []
    final.append(annotation[0])
    final.append(annotation[1])

    zipped = zip(COLUMNS[2:], annotation[2:], review[::2], resolution)
    for column, annotation_part, review_part, resolution_part in zipped:
        assert_column_value(column, annotation_part)
        assert_column_value(column, review_part, allow="*")
        assert_column_value(column, resolution_part, allow="*-+")

        if resolution_part in ["*", "+"]:
            final_part = review_part
        elif resolution_part == "-":
            final_part = annotation_part
        else:
            final_part = resolution_part

        if final_part == "*":
            final_part = annotation_part

        final.append(final_part)

    return final


def is_data_line(line):
    """Decide whether a line contains annotation data."""
    return not (line == "" or line.startswith("#"))


def split_data_line(line):
    """Split a data line into its parts."""
    fields = line.split("\t")
    ParseException.unless(len(COLUMNS) <= len(fields) <= len(COLUMNS) + 3,
                          "Wrong number of columns {}".format(len(COLUMNS)))

    annotation = []
    review = None
    resolution = None

    for field, column in zip(fields, COLUMNS):
        annotation.append(fields.pop(0))
    if fields:
        review_str = fields.pop(0)
        # Handle incorrect leading space.
        if review_str.startswith("# "):
            review_str = "#" + review_str[2:]
        review = review_str.replace("*", "* NONE").split(" ")
        ParseException.unless(review[0][0] in ["#", "@"],
                              "Review must start with # or @")
        review[0] = review[0][1:] # Cleave off initial "#".
        ParseException.unless(len(review) == (len(annotation) - 2) * 2,
                              "Review wrong length")
    if fields:
        resolution = fields.pop(0).split(" ")
        if len(resolution) != 1:
            ParseException.unless(len(resolution) == len(COLUMNS) - 2,
                                  "Resolution wrong length")
    return (annotation, review, resolution)


def process_line(line, line_num):
    line = line.strip()
    if is_data_line(line):
        annotation, review, resolution = split_data_line(line)
        if review and resolution:
            resolved_annotation = resolve(annotation, review, resolution)
            return "\t".join(resolved_annotation)
    return line


def process_file(input_path, output_path):
    with open(input_path, "r") as in_file, open(output_path, "w") as out_file:
        for line_num, line in enumerate([""] + in_file.readlines()):
            if line_num == 0:
                continue
            try:
                out_line = process_line(line, line_num)
                out_file.write(out_line + "\n")
            except (ResolveException, ParseException) as ex:
                print "line {}: {}".format(line_num, repr(ex))
                out_file.write(line.strip() + "\n")


if __name__ == "__main__":
    arguments = docopt(__doc__)
    input_path = arguments["<input-path>"]
    output_path = arguments["<output-path>"]
    process_file(input_path, output_path)
    print "\nOutput written to {}".format(output_path)
