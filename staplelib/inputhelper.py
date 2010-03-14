"""Helper functions for user-supplied arguments."""

import os.path
import re

from . import CommandError


def check_input_files(files):
    """Make sure all input files exist."""

    for filename in files:
        if not os.path.exists(filename):
            raise CommandError("%s does not exist" % filename)


def check_output_file(filename):
    """Make sure the output file does not exist."""

    if os.path.exists(filename):
        raise CommandError("File already exists: %s" % filename)


def parse_ranges(files_and_ranges):
    """Parse a list of filenames followed by ranges."""

    operations = []
    for inputname in files_and_ranges:
        if (re.match('.*?\.pdf', inputname)):
            operations.append({"name":inputname,"pages":[]})
        else:
            if (re.match('[0-9]+-[0-9]+', inputname)):
                (begin,sep,end) = inputname.partition("-")
                for j in range(int(begin), int(end)+1):
                    operations[-1]["pages"].append(int(j))
            else:
                operations[-1]["pages"].append(int(inputname))

    check_input_files([ f['name'] for f in operations ])

    return operations
