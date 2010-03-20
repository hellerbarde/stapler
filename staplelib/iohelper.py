"""Helper functions for user-supplied arguments and file I/O."""

import os.path
import re

from pyPdf import PdfFileWriter, PdfFileReader

from . import CommandError


def read_pdf(filename):
    """Open a PDF file with pyPdf."""
    if not os.path.exists(filename):
        raise CommandError("%s does not exist" % filename)
    return PdfFileReader(file(filename, "rb"))


def write_pdf(pdf, filename):
    """Write the content of a PdfFileWriter object to a file."""
    if os.path.exists(filename):
        raise CommandError("File already exists: %s" % filename)

    outputStream = file(filename, "wb")
    pdf.write(outputStream)
    outputStream.close()


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
            operations.append({"name": inputname,
                               "pdf": read_pdf(inputname),
                               "pages": []})
        else:
            match = re.match('([0-9]+|end)(?:-([0-9]+|end))?', inputname)
            if not match:
                raise CommandError('Invalid range: %s' % inputname)

            # allow "end" as alias for the last page
            replace_end = lambda page: (
                operations[-1]['pdf'].getNumPages() if page == 'end' else
                int(page))
            begin = replace_end(match.group(1))
            end = replace_end(match.group(2)) if match.group(2) else begin

            # negative ranges sort pages backwards
            if begin < end:
                pagerange = range(begin, end+1)
            else:
                pagerange = range(end, begin+1)[::-1]

            operations[-1]['pages'] += pagerange

    return operations
