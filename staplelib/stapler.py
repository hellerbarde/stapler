#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main stapler dispatcher."""

from optparse import OptionParser
import sys

from . import commands, CommandError


USAGE = """usage: %prog [options] mode input.pdf ... [output.pdf]

Modes:
burst/split: create one file per page in input pdf files (no output needed)
cat/sel: <inputfile> [<pagerange>] ... (output needed)
     Select the given pages/ranges from input files.
     No range means all pages.
del: <inputfile> [<pagerange>] ... (output needed)
     Select all but the given pages/ranges from input files.

Page ranges:
    n - single numbers mean single pages (e.g., 15)
    n-m - page ranges include the entire specified range (e.g. 1-6)
    m-n - negative ranges sort pages backwards (e.g. 6-3)
"""


def main():
    """
    Handle all command line arguments and pass them on to the respective
    commands.
    """
    parser = OptionParser(usage=USAGE)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False)
    (options, args) = parser.parse_args()

    if (len(args) < 2):
        print "Error: Not enough arguments"
        parser.print_help()
        sys.exit(1)

    modes = {
        "cat": commands.select,
        "sel": commands.select,
        "split": commands.split,
        "burst": commands.split,
        "del": commands.delete,
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
