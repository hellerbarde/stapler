"""Module containing the actual commands stapler understands."""

from os.path import splitext
import math

# pyPdf is using some code deprecated in Python 2.6.
# That's sad, but no need to bug the user with it.
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

from pyPdf import PdfFileWriter, PdfFileReader

from . import CommandError, inputhelper


def concatenate(options, args):
    infilenames = args[:-1]
    outputfilename = args[-1]
    verbose = options.verbose

    if not infilenames or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    inputhelper.check_input_files(infilenames)
    inputhelper.check_output_file(outputfilename)

    inputs = []
    for infile in infilenames:
        print infile
        try:
            inputs.append(PdfFileReader(file(infile, "rb")))
        except Exception, e:
            raise CommandError(e)

    output = PdfFileWriter()

    pagecount = 0
    for pdf in inputs:
        for pagenr in range(pdf.getNumPages()):
            output.addPage(pdf.getPage(pagenr))
            pagecount += 1
    outputStream = file(outputfilename, "wb")
    output.write(outputStream)
    outputStream.close()

    if verbose:
        print
        print "%s page(s) processed" % pagecount


def split(options, args):
    files = args
    verbose = options.verbose

    if not files:
        raise CommandError("No input files specified.")

    inputhelper.check_input_files(files)

    inputs = []
    try:
        for i in files:
            inputs.append(PdfFileReader(file(i, "rb")))
    except Exception, e:
        raise CommandError(e)

    filecount=0
    pagecount=0
    for pdf in inputs:
        for pagenr in range(pdf.getNumPages()):
            output = PdfFileWriter()
            output.addPage(pdf.getPage(pagenr))

            (name, ext) = splitext(files[filecount])
            my_str = "%0" + str(math.ceil(math.log10(pdf.getNumPages()))) + "d"
            my_str = my_str % (pagenr+1)
            if verbose:
                print (name+"p"+my_str+ext)
            outputStream = file(name+"p"+my_str+ext, "wb")
            output.write(outputStream)
            outputStream.close()
            pagecount += 1
        filecount += 1

    if verbose:
        print
        print "%d page(s) in %d file(s) processed." % (pagecount, filecount)


def select(options, args):
    filesandranges = inputhelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = options.verbose

    if not filesandranges or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    inputhelper.check_output_file(outputfilename)

    output = PdfFileWriter()
    try:
        for pdf in filesandranges:
            fiel = PdfFileReader(file(pdf["name"], "rb"))
            if verbose:
                print pdf['name']

            for pagenr in pdf["pages"]:
                if (not (pagenr > fiel.getNumPages()) and not(pagenr < 1)):
                    if verbose:
                        print "Using page: %d" % pagenr
                    output.addPage(fiel.getPage(pagenr-1))
                else:
                    raise CommandError(
                        "Page %d not found in %s." % (pagenr, pdf['name']))
    except Exception, e:
        raise CommandError(e)

    outputStream = file(outputfilename, "wb")
    output.write(outputStream)
    outputStream.close()


def delete(options, args):
    filesandranges = inputhelper.parse_ranges(args[:-1])
    outputfilename = args[-1]
    verbose = options.verbose

    if not filesandranges or not outputfilename:
        raise CommandError("Both input and output filenames are required.")

    inputhelper.check_output_file(outputfilename)

    output = PdfFileWriter()
    try:
        for pdf in filesandranges:
            if verbose:
                print pdf["name"]
            fiel = PdfFileReader(file(pdf["name"], "rb"))

            for pagenr in range(1,fiel.getNumPages()+1):
                if (pagenr not in pdf["pages"]):
                    output.addPage(fiel.getPage(pagenr-1))
                elif verbose:
                    print "Skipping page: %d" % pagenr
    except Exception, e:
        raise CommandError(e)

    outputStream = file(outputfilename, "wb")
    output.write(outputStream)
    outputStream.close()
