"""Module containing the actual commands stapler understands."""
import math
import os

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader
except:
    from pyPdf import PdfFileWriter, PdfFileReader
import itertools
import more_itertools

from . import CommandError, iohelper
import staplelib

def select(args, inverse=False, even_page=False):
    """
    Concatenate files / select pages from files.

    inverse=True excludes rather than includes the selected pages from
    the file.
    even_page=True inserts an empty page at the end of each input
    file if it ends with an odd page number.
    """

    filesandranges = iohelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = staplelib.OPTIONS.verbose

    if not filesandranges or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    output = PdfFileWriter()
    pagecnt = 0
    try:
        for input in filesandranges:
            pdf = input['pdf']
            if verbose:
                print input['name']

            # empty range means "include all pages"
            if not inverse:
                pagerange = input['pages'] or [
                    (p, iohelper.ROTATION_NONE) for p in
                    range(1, pdf.getNumPages() + 1)]
            else:
                excluded = [p for p, r in input['pages']]
                pagerange = [(p, iohelper.ROTATION_NONE) for p in
                             range(1, pdf.getNumPages() + 1) if
                             p not in excluded]

            for pageno, rotate in pagerange:
                if 1 <= pageno <= pdf.getNumPages():
                    if verbose:
                        print "Using page: {} (rotation: {} deg.)".format(
                            pageno, rotate)

                    page = pdf.getPage(pageno-1)
                    output.addPage(page.rotateClockwise(rotate))
                    pagecnt += 1
                else:
                    raise CommandError("Page {} not found in {}.".format(
                        pageno, input['name']))

            if even_page:
                if pagecnt % 2 == 1:
                    output.addPage(iohelper.create_empty_page(page))
                    pagecnt += 1

    except Exception, e:
        raise CommandError(e)

    if os.path.isabs(outputfilename):
        iohelper.write_pdf(output, outputfilename)
    else:
        iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                           os.sep + outputfilename)

def select_even(args, inverse=False):
    """
    Concatenate files / select pages from files.

    Inserts an empty page at the end of each input file if it ends with
    an odd page number.
    """

    select(args, inverse, True)


def delete(args):
    """Concatenate files and remove pages from files."""
    return select(args, inverse=True)


def split(args):
    """Burst an input file into one file per page."""
    files = args
    verbose = staplelib.OPTIONS.verbose

    if not files:
        raise CommandError("No input files specified.")

    inputs = []
    try:
        for f in files:
            inputs.append(iohelper.read_pdf(f))
    except Exception, e:
        raise CommandError(e)

    filecount = 0
    pagecount = 0
    for input in inputs:
        # zero-padded output file name
        (base, ext) = os.path.splitext(os.path.basename(files[filecount]))
        output_template = ''.join([
            base,
            '_',
            '%0',
            str(math.ceil(math.log10(input.getNumPages()))),
            'd',
            ext
        ])

        for pageno in range(input.getNumPages()):
            output = PdfFileWriter()
            output.addPage(input.getPage(pageno))

            outputname = output_template % (pageno + 1)
            if verbose:
                print outputname
            iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                               os.sep + outputname)
            pagecount += 1
        filecount += 1

    if verbose:
        print "\n{} page(s) in {} file(s) processed.".format(
            pagecount, filecount)


def info(args):
    """Display Metadata content for all input files."""
    files = args

    if not files:
        raise CommandError("No input files specified.")

    for f in files:
        pdf = iohelper.read_pdf(f)
        print "*** Metadata for {}".format(f)
        print
        info = pdf.documentInfo
        if info:
            for name, value in info.items():
                print u"    {}:  {}".format(name, value)
        else:
            print "    (No metadata found.)"
        print

def background(args):
    """Combine 2 files with corresponding pages merged."""

    filesandranges = iohelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = staplelib.OPTIONS.verbose

    if not filesandranges or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    try:
        filestozip = []
        for input in filesandranges:
            pdf = input['pdf']
            if verbose:
                print input['name']

            # empty range means "include all pages"
            pagerange = input['pages'] or [
                (p, iohelper.ROTATION_NONE) for p in
                range(1, pdf.getNumPages() + 1)]

            pagestozip = []
            for pageno, rotate in pagerange:
                if 1 <= pageno <= pdf.getNumPages():
                    if verbose:
                        print "Using page: {} (rotation: {} deg.)".format(
                            pageno, rotate)

                    pagestozip.append(pdf.getPage(pageno-1)
                                   .rotateClockwise(rotate))
                else:
                    raise CommandError("Page {} not found in {}.".format(
                        pageno, input['name']))
            filestozip.append(pagestozip)

        output = PdfFileWriter()
        for pagelist in list(itertools.izip_longest(*filestozip)):
            page = pagelist[0]
            for p in pagelist[1:]:
              if not page:
                page = p
              elif p:
                page.mergePage(p)
            output.addPage(page)

    except Exception, e:
        import sys
        import traceback
        traceback.print_tb(sys.exc_info()[2])
        raise CommandError(e)

    if os.path.isabs(outputfilename):
        iohelper.write_pdf(output, outputfilename)
    else:
        iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                           os.sep + outputfilename)

def zip(args):
    """Combine 2 files with interleaved pages."""
    filesandranges = iohelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = staplelib.OPTIONS.verbose

    if not filesandranges or not outputfilename:
        raise CommandError('Both input and output filenames are required.')

    # Make [[file1_p1, file1_p2], [file2_p1, file2_p2], ...].
    filestozip = []
    for input in filesandranges:
        pdf = input['pdf']
        if verbose:
            print input['name']

        # Empty range means "include all pages".
        pagerange = input['pages'] or [
            (p, iohelper.ROTATION_NONE) for p in
            range(1, pdf.getNumPages() + 1)]

        pagestozip = []
        for pageno, rotate in pagerange:
            if 1 <= pageno <= pdf.getNumPages():
                if verbose:
                    print "Using page: {} (rotation: {} deg.)".format(
                        pageno, rotate)

                pagestozip.append(
                    pdf.getPage(pageno - 1).rotateClockwise(rotate))
            else:
                raise CommandError("Page {} not found in {}.".format(
                    pageno, input['name']))
        filestozip.append(pagestozip)

    # Interweave pages.
    output = PdfFileWriter()
    for page in more_itertools.roundrobin(*filestozip):
        output.addPage(page)

    if os.path.isabs(outputfilename):
        iohelper.write_pdf(output, outputfilename)
    else:
        iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                           os.sep + outputfilename)
