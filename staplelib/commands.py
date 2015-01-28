"""Module containing the actual commands stapler understands."""

import math
import os.path
import os
import itertools

from PyPDF2 import PdfFileWriter, PdfFileReader

from . import CommandError, iohelper
import staplelib


def roundrobinLIST(iterables):
    "roundrobinLIST(['ABC', 'D', 'EF']) --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


def zip(args):
    """Combine 2 files with interleaved pages."""

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
        for page in list(roundrobinLIST(filestozip)):
            output.addPage(page)

    except Exception, e:
        raise CommandError(e)

    if os.path.isabs(outputfilename):
        iohelper.write_pdf(output, outputfilename)
    else:
        iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                           os.sep + outputfilename)


def select(args, inverse=False):
    """
    Concatenate files / select pages from files.

    inverse=True excludes rather than includes the selected pages from
    the file.
    """

    filesandranges = iohelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = staplelib.OPTIONS.verbose

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
                    
                    output.addPage(pdf.getPage(pageno-1)
                                   .rotateClockwise(rotate))
                else:
                    raise CommandError("Page {} not found in {}.".format(
                        pageno, input['name']))

    except Exception, e:
        raise CommandError(e)

    if os.path.isabs(outputfilename):
        iohelper.write_pdf(output, outputfilename)
    else:
        iohelper.write_pdf(output, staplelib.OPTIONS.destdir + 
                           os.sep + outputfilename)


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
