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
        if inputname.lower().endswith('.pdf'):
            operations.append({"name": inputname, "pages": []})
        else:
            match = re.match('([0-9]+)(?:-([0-9]+))?', inputname)
            if not match:
                raise CommandError('Invalid range: %s' % inputname)

            begin = int(match.group(1))
            end = int(match.group(2) or begin) # "8" == "8-8"

            # negative ranges sort pages backwards
            if begin < end:
                pagerange = range(begin, end+1)
            else:
                pagerange = range(end, begin+1)[::-1]

            operations[-1]['pages'] += pagerange

    check_input_files([ f['name'] for f in operations ])

    return operations
