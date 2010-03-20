"""Module containing the actual commands stapler understands."""

import math
import os.path

from pyPdf import PdfFileWriter, PdfFileReader

from . import CommandError, iohelper


def select(options, args, inverse=False):
    """
    Concatenate files / select pages from files.

    inverse=True excludes rather than includes the selected pages from
    the file.
    """

    filesandranges = iohelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = options.verbose

    if not filesandranges or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    output = PdfFileWriter()
    try:
        for input in filesandranges:
            pdf = input['pdf']
            if verbose:
                print input['name']

            # empty range means "include all pages"
            if not inverse:
                pagerange = input['pages'] or range(1, pdf.getNumPages()+1)
            else:
                pagerange = [p for p in range(1, pdf.getNumPages()+1) if
                             p not in input['pages']]

            for pageno in pagerange:
                if 1 <= pageno <= pdf.getNumPages():
                    if verbose:
                        print "Using page: %d" % pageno
                    output.addPage(pdf.getPage(pageno-1))
                else:
                    raise CommandError(
                        "Page %d not found in %s." % (pageno, input['name']))

    except Exception, e:
        raise CommandError(e)

    iohelper.write_pdf(output, outputfilename)


def delete(options, args):
    """Concatenate files and remove pages from files."""

    return select(options, args, inverse=True)


def split(options, args):
    """Burst an input file into one file per page."""

    files = args
    verbose = options.verbose

    if not files:
        raise CommandError("No input files specified.")

    inputs = []
    try:
        for f in files:
            inputs.append(iohelper.read_pdf(i))
    except Exception, e:
        raise CommandError(e)

    filecount = 0
    pagecount = 0
    for input in inputs:
        # zero-padded output file name
        (base, ext) = os.path.splitext(os.path.basename(files[filecount]))
        output_template = ''.join([
            base, '_',
            '%0', str(math.ceil(math.log10(input.getNumPages()))), 'd',
            ext
        ])

        for pageno in range(input.getNumPages()):
            output = PdfFileWriter()
            output.addPage(input.getPage(pageno))

            outputname = output_template % (pageno+1)
            if verbose:
                print outputname
            iohelper.write_pdf(output, outputname)

            pagecount += 1
        filecount += 1

    if verbose:
        print
        print "%d page(s) in %d file(s) processed." % (pagecount, filecount)

