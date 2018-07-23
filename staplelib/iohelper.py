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

HANDLES = {}

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
    force = staplelib.OPTIONS.force

    """Write the content of a PdfFileWriter object to a file."""
    if os.path.exists(filename) and not force:
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


def parse_ranges(handles_files_and_ranges):
    """Parse a list of filenames followed by ranges."""

    operations = []
    handle_pattern = re.compile('^[A-Z]=')
    for inputname in handles_files_and_ranges:
        handle_key = None
        handle_value = None
        if handle_pattern.match(inputname):
            handle_key,handle_value = inputname.split("=",2)
            HANDLES[handle_key] = handle_value
        elif inputname.lower().endswith('.pdf'):
            operations.append({"name": inputname,
                               "pdf": read_pdf(inputname),
                               "pages": []})
        else:
            handle_key = None
            handle_value = None
            match = re.match('([A-Z])?([0-9]+|end)(?:-([0-9]+|end))?(even|odd)?([LRD]?)',
                                inputname)
            if not match:
                raise CommandError('Invalid range: {}'.format(inputname))

            if match.group(1):
                handle_key = match.group(1)
                if handle_key in HANDLES:
                    handle_value = HANDLES[handle_key]
                    operations.append({"name": handle_value,
                                       "pdf": read_pdf(handle_value),
                                       "pages": []})
                else:
                    raise CommandError(
                        "Filehandle '{}' does not exist in "
                        "page range '{}'".format(handle_key, inputname))

            current = operations[-1]
            max_page = current['pdf'].getNumPages()
            step_size = 1
            # allow "end" as alias for the last page
            replace_end = lambda page: (
                max_page if page.lower() == 'end' else int(page))
            begin = replace_end(match.group(2))
            end = replace_end(match.group(3)) if match.group(3) else begin

            page_subset = match.group(4) if match.group(4) else 'all'

            begin_is_odd = False
            if begin % 2 == 1:
                begin_is_odd = True

            if begin == end:
                page_subset = 'all'

            if page_subset == 'even' or page_subset == 'odd':
                step_size = 2

            rotate = ROTATIONS.get((match.group(5) or 'u').lower())

            if begin > max_page or end > max_page:
                raise CommandError(
                    "Range {}-{} exceeds maximum page number "
                    "{} of file {}".format(
                        begin, end, max_page, current['name']))

            if begin < 1 or end < 1:
                raise CommandError(
                    "Range {}-{} subceeds minimum page number "
                    "1 of file {}".format(
                        begin, end, current['name']))

            if begin > end:
                if page_subset == 'even' and begin_is_odd == True:
                    begin -= 1
                if page_subset == 'odd' and begin_is_odd == False:
                    begin -= 1
                pagerange = range(begin, end - 1, step_size * -1)
            else:
                if page_subset == 'even' and begin_is_odd == True:
                    begin += 1
                if page_subset == 'odd' and begin_is_odd == False:
                    begin += 1
                pagerange = range(begin, end + 1, step_size)

            for p in pagerange:
                current['pages'].append((p, rotate))

    return operations
