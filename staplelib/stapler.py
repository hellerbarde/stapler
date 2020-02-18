#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main stapler dispatcher."""

from __future__ import print_function

import os
import sys
from argparse import ArgumentParser

import staplelib
from . import commands, CommandError

USAGE = """
usage: %(prog)s [options] mode (input.pdf|input handle) ... [output.pdf]

Modes:
cat/sel: <inputfile>|<input handle> [<pagerange>[<rotation>]] ... (output needed)
    Select the given pages/ranges from input files.
    No range means all pages.
del: <inputfile> [<pagerange>[<rotation>]] ... (output needed)
    Select all but the given pages/ranges from input files.
burst/split: <inputfile> ... (no output needed)
    Create one file per page in input pdf files (no output needed)
zip: <inputfile>|<input handle> [<pagerange>[<rotation>]] ... (output needed)
    Merge/Collate the given input files interleaved.
background: <inputfile> [<pagerange>[<rotation>]] ... (output needed)
    Merge/Overlay the given input files interleaved.
info: <inputfile> ... (no output needed)
    Display PDF metadata
list-log(ical): <inputfile>
    Display the logical names of each page.

Input handle:
    A single, upper-case letter as an alias to a file
    For example: A=input1.pdf B=input2.pdf

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
argparser = ArgumentParser(usage=USAGE)
argparser.add_argument('-o', '--ownerpw',
                       action='store',
                       dest='ownerpw',
                       help='Set owner password to encrypt output file with',
                       default=None)
argparser.add_argument('-u', '--userpw',
                       action='store',
                       dest='userpw',
                       help='Set user password to encrypt output file with',
                       default=None)
argparser.add_argument('-v', '--verbose',
                       action='store_true',
                       dest='verbose',
                       default=False)
argparser.add_argument('-f', '--force',
                       action='store_true',
                       dest='force',
                       help='Overwrite output file if it exists',
                       default=False)
argparser.add_argument('-d', '--destdir',
                       dest="destdir",
                       default="." + os.sep,
                       help="directory where to store output file", )
argparser.add_argument('mode',
                       action='store',
                       help="requested stapler mode")


def main(arguments=None):
    """
    Handle all command line arguments and pass them on to the respective
    commands.
    """

    if not arguments:
        arguments = sys.argv[1:]

    (staplelib.OPTIONS, args) = argparser.parse_known_args(args=arguments)

    if not os.path.exists(staplelib.OPTIONS.destdir):
        print_error_and_exit("cannot find output directory named {}".format(
            staplelib.OPTIONS.destdir))

    if (len(args) < 1):
        print_error_and_exit("Not enough arguments", show_usage=True)

    modes = {
        "cat": commands.select,
        "sel": commands.select,
        "split": commands.split,
        "burst": commands.split,
        "del": commands.delete,
        "info": commands.info,
        "zip": commands.zip,
        "background": commands.background,
        "list-log": commands.list_logical_pages,
        "list-logical": commands.list_logical_pages,
    }

    mode = staplelib.OPTIONS.mode

    if mode not in modes:
        print_error_and_exit('Please enter a valid mode', show_usage=True)

    if staplelib.OPTIONS.verbose:
        print("Mode: %s" % mode)

    # dispatch call to known subcommand
    try:
        modes[mode](args)
    except CommandError as e:
        print_error_and_exit(e)


def print_error_and_exit(msg, code=1, show_usage=False):
    """Pretty-print an error to the user."""
    sys.stderr.write(str('Error: {}\n'.format(msg)))

    if show_usage:
        argparser.print_usage(sys.stderr)

    sys.exit(code)
