#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main stapler dispatcher."""

from optparse import OptionParser
import os
import sys

from . import commands, CommandError
import staplelib


USAGE = """
usage: %prog [options] mode input.pdf ... [output.pdf]

Modes:
cat/sel: <inputfile> [<pagerange>] ... (output needed)
    Select the given pages/ranges from input files.
    No range means all pages.
del: <inputfile> [<pagerange>[<rotation>]] ... (output needed)
    Select all but the given pages/ranges from input files.
burst/split: <inputfile> ... (no output needed)
    Create one file per page in input pdf files (no output needed)
zip: <inputfile> [<pagerange>[<rotation>]] ... (output needed)
    Merge/Collate the given input files interleaved.
info: <inputfile> ... (no output needed)
    Display PDF metadata

Page ranges:
    n - single numbers mean single pages (e.g., 15)
    n-m - page ranges include the entire specified range (e.g. 1-6)
    m-n - negative ranges sort pages backwards (e.g., 6-3)

Extended page range options:
    ...-end will be replaced with the last page in the file
    R, L, or D will rotate the respective range +90, -90, or 180 degrees,
        respectively. (e.g., 1-15R)
""".strip()

# command line option parser
parser = OptionParser(usage=USAGE)
parser.add_option('-o', '--ownerpw', action='store', dest='ownerpw',
                  help='Set owner password to encrypt output file with',
                  default=None)
parser.add_option('-u', '--userpw', action='store', dest='userpw',
                  help='Set user password to encrypt output file with',
                  default=None)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                  default=False)
parser.add_option('-d', '--destdir', dest="destdir", default="." + os.sep,
                  help="directory where to store output file",)


def main():
    """
    Handle all command line arguments and pass them on to the respective
    commands.
    """
    (staplelib.OPTIONS, args) = parser.parse_args()

    if not os.path.exists(staplelib.OPTIONS.destdir):
        print_error("cannot find output directory named {}".format(
                    staplelib.OPTIONS.destdir))

    if (len(args) < 2):
        print_error("Not enough arguments", show_usage=True)

    modes = {
        "cat": commands.select,
        "sel": commands.select,
        "split": commands.split,
        "burst": commands.split,
        "del": commands.delete,
        "info": commands.info,
        "zip": commands.zip,
    }

    mode = args[0]
    args = args[1:]
    if not mode in modes:
        print_error('Please enter a valid mode', show_usage=True)

    if staplelib.OPTIONS.verbose:
        print "Mode: %s" % mode

    # dispatch call to known subcommand
    try:
        modes[mode](args)
    except CommandError, e:
        print_error(e)


def print_error(msg, code=1, show_usage=False):
    """Pretty-print an error to the user."""
    sys.stderr.write(str('Error: {}\n'.format(msg)))

    if show_usage:
        sys.stderr.write("\n{}\n".format(parser.get_usage()))

    sys.exit(code)
