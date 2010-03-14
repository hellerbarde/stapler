#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main stapler dispatcher."""

from optparse import OptionParser
import sys

from . import commands


def main():
    """
    Handle all command line arguments and pass them on to the respective
    commands.
    """

    usage = """usage: %prog [options] mode input.pdf ... [output.pdf]
    Modes:
    cat: concatenate all input pdf files (output is needed for this mode)
    split: create one file per page in input pdf files (no output needed)
    sel: <inputfile> <pagenr>|<pagerange> ... (output needed)
         Select the given pages/ranges from input files
    del: <inputfile> <pagenr>|<pagerange> ... (output needed)
         Select all but the given pages/ranges from input files"""
    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False)
    (options, args) = parser.parse_args()

    if (len(args) < 2):
        print "Error: Not enough arguments"
        parser.print_help()
        sys.exit(1)

    modes = {
        "cat": commands.concatenate,
        "split": commands.split,
        "del": commands.delete,
        "sel": commands.select
    }

    mode = args[0]
    args = args[1:]
    if not mode in modes:
        print "Error: Please enter a valid mode"
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        print "Mode: %s" % mode

    # dispatch call to known subcommand
    try:
        modes[mode](options=options, args=args)
    except CommandError, e:
        sys.stderr.write(str('Error: %s\n' % e))
        sys.exit(1)
