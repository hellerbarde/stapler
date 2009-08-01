#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Philip Stark
# BSD Style Licence

from pyPdf import PdfFileWriter, PdfFileReader
import sys
import re
#####################################
# Handle all command line arguments #
#####################################
def parse_args(argv):
	mode = ""
	# Possible modes are:
	# cat   - concatenate multiple PDFs
	# split - split a pdf into single pages
	# del   - delete single pages or ranges
	# sel   - select single pages or ranges (opposite of del)

	modes = ["cat", "split", "del", "sel"]

	if (len(argv) < 3):
		print "too few arguments"
		#usage()
		sys.exit()

	mode = argv[1]
	files = argv[2:]
	if (mode in modes):
		print "mode: "+mode
	else:
		print "please input a valid mode"
		print files
		sys.exit()

	print files

	if (mode == "cat"):
		cat(files)
	elif (mode == "split"):
		split(files)
	elif (mode == "del"):
		delete(files)
	elif (mode == "sel"):
		select(files)

	outfile = ""

#	if (re.match('.*?\.pdf', arguments[-1])):
#		print "out: " + arguments[-1]
#		outfile = arguments[-1]
#	else:
#		print "target not specified correctly (needs to end in .pdf)"
#		sys.exit()


### end parse_args ###

def cat(files):
	inputs = []
	outputfilename = files[-1]
	output = PdfFileWriter()
	for i in files[:-1]:
		inputs.append(PdfFileReader(file(i, "rb")))

	for pdf in inputs:
		for pagenr in range(pdf.getNumPages()):
			output.addPage(pdf.getPage(pagenr))
	outputStream = file(outputfilename, "wb")
	output.write(outputStream)
	outputStream.close()
###### end cat ######

def split(args):
	pass
###### end split ######

def delete(args):
	pass
###### end delete ######

def select(args):
	pass
###### end select ######
# add page 1 from input1 to output document, unchanged
# output.addPage(input1.getPage(0))

# add page 2 from input1, but rotated clockwise 90 degrees
#output.addPage(input1.getPage(1).rotateClockwise(90))

# add page 3 from input1, rotated the other way:
#output.addPage(input1.getPage(2).rotateCounterClockwise(90))
# alt: output.addPage(input1.getPage(2).rotateClockwise(270))

# add page 4 from input1, but first add a watermark from another pdf:
#page4 = input1.getPage(3)
#watermark = PdfFileReader(file("watermark.pdf", "rb"))
#page4.mergePage(watermark.getPage(0))

# add page 5 from input1, but crop it to half size:
#page5 = input1.getPage(4)
#page5.mediaBox.upperRight = (
#    page5.mediaBox.getUpperRight_x() / 2,
#    page5.mediaBox.getUpperRight_y() / 2
#)
#output.addPage(page5)

# print how many pages input1 has:
#print "document1.pdf has %s pages." % input1.getNumPages()

# finally, write "output" to document-output.pdf
parse_args(sys.argv)

