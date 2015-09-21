"""Helper functions for user-supplied arguments and file I/O."""

import getpass
import os.path
import re
import sys

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader
except ImportError:
    from pyPdf import PdfFileWriter, PdfFileReader


from . import CommandError
import staplelib


ROTATION_NONE = 0
ROTATION_RIGHT = 90
ROTATION_TURN = 180
ROTATION_LEFT = 270
ROTATIONS = {'u': ROTATION_NONE,
             'r': ROTATION_RIGHT,
             'd': ROTATION_TURN,
             'l': ROTATION_LEFT}


def read_pdf(filename):
    """Open a PDF file with PyPDF2."""
    if not os.path.exists(filename):
        raise CommandError("{} does not exist".format(filename))
    pdf = PdfFileReader(file(filename, "rb"))
    if pdf.isEncrypted:
        while True:
            pw = prompt_for_pw(filename)
            matched = pdf.decrypt(pw)
            if matched:
                break
            else:
                print "The password did not match."
    return pdf


def write_pdf(pdf, filename):
    """Write the content of a PdfFileWriter object to a file."""
    if os.path.exists(filename):
        raise CommandError("File already exists: {}".format(filename))

    opt = staplelib.OPTIONS
    if opt:
        if opt.ownerpw or opt.userpw:
            pdf.encrypt(opt.userpw or '', opt.ownerpw)

    outputStream = file(filename, "wb")
    pdf.write(outputStream)
    outputStream.close()


def prompt_for_pw(filename):
    """Prompt the user for the password to access an input file."""
    print 'Please enter a password to decrypt {}.'.format(filename)
    print '(The password will not be shown. Press ^C to cancel).'

    try:
        return getpass.getpass('--> ')
    except KeyboardInterrupt:
        sys.stderr.write('Aborted by user.\n')
        sys.exit(2)


def check_input_files(files):
    """Make sure all input files exist."""

    for filename in files:
        if not os.path.exists(filename):
            raise CommandError("{} does not exist".format(filename))


def check_output_file(filename):
    """Make sure the output file does not exist."""

    if os.path.exists(filename):
        raise CommandError("File already exists: {}".format(filename))


def parse_ranges(files_and_ranges):
    """Parse a list of filenames followed by ranges."""

    operations = []
    for inputname in files_and_ranges:
        if inputname.lower().endswith('.pdf'):
            operations.append({"name": inputname,
                               "pdf": read_pdf(inputname),
                               "pages": []})
        else:
            match = re.match('([0-9]+|end)(?:-([0-9]+|end))?([LRD]?)',
                                inputname)
            if not match:
                raise CommandError('Invalid range: {}'.format(inputname))

            current = operations[-1]
            max_page = current['pdf'].getNumPages()
            # allow "end" as alias for the last page
            replace_end = lambda page: (
                max_page if page.lower() == 'end' else int(page))
            begin = replace_end(match.group(1))
            end = replace_end(match.group(2)) if match.group(2) else begin

            rotate = ROTATIONS.get((match.group(3) or 'u').lower())

            if begin > max_page or end > max_page:
                raise CommandError(
                    "Range {}-{} exceeds maximum page number "
                    "{} of file {}".format(
                        begin, end, max_page, current['name']))

            # negative ranges sort pages backwards
            if begin < end:
                pagerange = range(begin, end + 1)
            else:
                pagerange = range(end, begin + 1)[::-1]

            for p in pagerange:
                current['pages'].append((p, rotate))

    return operations
