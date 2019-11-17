"""Module containing the actual commands stapler understands."""
from __future__ import print_function
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
                print(input['name'])

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
                        print("Using page: {} (rotation: {} deg.)".format(
                            pageno, rotate))

                    output.addPage(pdf.getPage(pageno-1)
                                   .rotateClockwise(rotate))
                else:
                    raise CommandError("Page {} not found in {}.".format(
                        pageno, input['name']))

    except Exception as e:
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
    except Exception as e:
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
                print(outputname)
            iohelper.write_pdf(output, staplelib.OPTIONS.destdir +
                               os.sep + outputname)
            pagecount += 1
        filecount += 1

    if verbose:
        print("\n{} page(s) in {} file(s) processed.".format(
            pagecount, filecount))


def info(args):
    """Display Metadata content for all input files."""
    files = args

    if not files:
        raise CommandError("No input files specified.")

    for f in files:
        pdf = iohelper.read_pdf(f)
        print("*** Metadata for {}".format(f))
        print()
        info = pdf.documentInfo
        if info:
            for name, value in info.items():
                print(u"    {}:  {}".format(name, value))
        else:
            print("    (No metadata found.)")
        print()

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
                print(input['name'])

            # empty range means "include all pages"
            pagerange = input['pages'] or [
                (p, iohelper.ROTATION_NONE) for p in
                range(1, pdf.getNumPages() + 1)]

            pagestozip = []
            for pageno, rotate in pagerange:
                if 1 <= pageno <= pdf.getNumPages():
                    if verbose:
                        print("Using page: {} (rotation: {} deg.)".format(
                            pageno, rotate))

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

    except Exception as e:
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
            print(input['name'])

        # Empty range means "include all pages".
        pagerange = input['pages'] or [
            (p, iohelper.ROTATION_NONE) for p in
            range(1, pdf.getNumPages() + 1)]

        pagestozip = []
        for pageno, rotate in pagerange:
            if 1 <= pageno <= pdf.getNumPages():
                if verbose:
                    print("Using page: {} (rotation: {} deg.)".format(
                        pageno, rotate))

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


def int_to_page_alpha(pageno, base):
    """return uppercase alphabetic page numbers for PAGENO starting at BASE (a or A).
Adobe defines them as A to Z, then AA to ZZ, and so on.
Yes, that is somewhat wacky."""
    (div, mod) = divmod( pageno-1, 26)
    c = chr(mod + ord(base))
    return c * (div+1)

# next text is from Paul M. Winkler
# via https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """

    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)



#
# pdf_page_enumeration is
# inspired by  https://stackoverflow.com/questions/12360999/retrieve-page-numbers-from-document-with-pypdf
# (thanks vjayky!)
# and informed by https://www.w3.org/TR/WCAG20-TECHS/PDF17.html
# (thanks, w3c!)
# which recaps the PDF-1.7 specification
# https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf
#
def pdf_page_enumeration(pdf):
    """Generate a list of pages, using /PageLabels (if it exists).  Returns a list of labels."""
    
    try:
        pagelabels = pdf.trailer["/Root"]["/PageLabels"]
    except:
        # ("No /Root/PageLabels object"), so infer the list.
        return range(1, pdf.getNumPages() + 1)
    
    # """Select the item that is most likely to contain the information you desire; e.g.
    #        {'/Nums': [0, IndirectObject(42, 0)]}
    #    here, we only have "/Num". """
    
    try:
        pagelabels_nums = pdf.trailer["/Root"]["/PageLabels"]["/Nums"]
    except:
        raise CommandError("Malformed PDF, /Root/PageLabels but no .../Nums object")

    #
    # At this point we have either the object or the list.
    # Make it a list.
    #
    if isinstance(pagelabels_nums, (list,)):
        pagelabels_nums_list = pagelabels_nums
    else:
        pagelabels_nums_list = list(pagelabels_nums)

    labels = []
    style = None
    # default
    style = '/D'
    prefix = ''
    next_pageno = 1
    for i in range(0, pdf.getNumPages()):
        if len(pagelabels_nums_list) > 0 and i >= pagelabels_nums_list[0]:
            pagelabels_nums_list.pop(0)  # discard index
            pnle = pagelabels_nums_list.pop(0)
            style = pnle.get('/S', '/D')
            prefix = pnle.get('/P', '')
            next_pageno = pnle.get('/St', 1)
        pageno_str = ''
        if style == '/D':
            pageno_str = str(next_pageno)
        elif style == '/A':
            pageno_str = int_to_page_alpha(next_pageno, 'A')
        elif style == '/a':
            pageno_str = int_to_page_alpha(next_pageno, 'a')
        elif style == '/R':
            pageno_str = int_to_roman(next_pageno)
        elif style == '/r':
            pageno_str = int_to_roman(next_pageno).lower()
        else:
            raise CommandError("Malformded PDF: unkown page numbering style " + style)
        labels.append(prefix + pageno_str)
        next_pageno += 1

    return labels


def list_logical_pages(args):
    """List the logical names of each page."""
    verbose = staplelib.OPTIONS.verbose

    files = args
    if not files:
        raise CommandError("An input filename is required.")

    try:
        for input in files:
            pdf = iohelper.read_pdf(input)
            if verbose:
                print(input)
            i = 0
            for label in pdf_page_enumeration(pdf):
                i += 1
                print("{}\t{}".format(label, str(i)))

    except Exception as e:
        raise CommandError(e)
