#!/usr/bin/env python3

from pokestring import pstring, format
import os

""" Preprocessor for assembly files """

DIRECTIVE_STRING = ".string" # example: '.string LANG "foo"'
DIRECTIVE_AUTOSTRING = ".autostring" # example: '.autostring LANG WIDTH HEIGHT "foo"'
DIRECTIVE_STRINGPAD = ".stringpad" # example: '.stringpad LANG LENGTH "foo"'


def preprocess_assembly(filepath, charmappath, outpath, language, terminator=0xFF):
    """ Preprocesses an assembly file. """


    ps = pstring.Pstring(charmappath, terminator=terminator)
    output = ""

    with open(filepath, "r", encoding="utf-8") as f:
        assembly = f.read()

    # Preprocess assembly linewise
    for line in splitlines_continued(assembly):

        # Normalize line by replacing
        # all tabs with whitespace
        # and cumulating consecutive 
        # whitespaces
        tokens = line.split()
        # Check for directives
        if len(tokens) < 1:
            output += os.linesep
        elif tokens[0] == DIRECTIVE_STRING:
            string = " ".join(tokens[2:])
            if language != tokens[1]:
                continue
            output += ".byte " + " ".join(
                map(str, process_string(string, ps))
            ) + os.linesep
        elif tokens[0] == DIRECTIVE_AUTOSTRING:
            string = " ".join(tokens[4])
            line_cnt = int(tokens[3], 0)
            linewidth = int(tokens[2], 0)
            if language != tokens[1]:
                continue
            bytes = process_string(string, ps)
            # Format string
            bytes = format.format_pstring(bytes, linewidth,
            line_cnt)
            output += ".byte " + " ".join(map(str, bytes)) + os.linesep
        elif tokens[0] == DIRECTIVE_STRINGPAD:
            padding = int(tokens[2], 0)
            string = " ".join(tokens[3:])
            if language != tokens[1]:
                continue
            bytes = process_string(string, ps)
            bytes += [0] * (padding - len(bytes))
            output += ".byte " + " ".join(map(str, bytes)) + os.linesep
        else:
            output += line + os.linesep

    with open(outpath, "w+", encoding="utf-8") as f:
        f.write(output)

        
def splitlines_continued(input):
    """ Yields lines continued by '\'."""
    for line in input.splitlines():
        line = line.rstrip(os.linesep)
        while line.endswith('\\'):
            line = line[:-1] + next(input).rstrip(os.linesep)
        yield line

def process_string(string, ps):
    """ Parses a .string directive string. """
    if string[0] != "\"" or \
        string[-1] != "\"":
        raise Exception("Expected strings to be \
        embedded into \"\" (token is {0})".format(string))

    return ps.str2hex(string[1:-1])
    





