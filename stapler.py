#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Philip Stark
# BSD Style Licence
import math
from pyPdf import PdfFileWriter, PdfFileReader
import sys
import re
import os.path
from os.path import splitext
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

def halp():
	print ("haaalp, something broke, but no worries, I will fix it (or not)")

def cat(files):
	inputs = []
	outputfilename = files[-1]
	output = PdfFileWriter()
	try: 
		for i in files[:-1]:
			inputs.append(PdfFileReader(file(i, "rb")))
	except:
		halp()
		sys.exit(2) # pdf file is no pdf file...
	i = 0
	for pdf in inputs:
		for pagenr in range(pdf.getNumPages()):
			output.addPage(pdf.getPage(pagenr))
			i=i+1
	outputStream = file(outputfilename, "wb")
	output.write(outputStream)
	outputStream.close()
	print (str(i)+" pages processed")
###### end cat ######

def split(files):
	inputs = []
	try:
		for i in files:
			inputs.append(PdfFileReader(file(i, "rb")))
	except:
		halp()
		sys.exit(2) # pdf file is no pdf file...
	i=0
	j=0
	for pdf in inputs:
		for pagenr in range(pdf.getNumPages()):
			output = PdfFileWriter()
			output.addPage(pdf.getPage(pagenr))
			(name, ext) = splitext(files[i])
			my_str = "%0" + str(math.ceil(math.log10(pdf.getNumPages()))) + "d"
			my_str = my_str % (pagenr+1)
			print (name+"p"+my_str+ext)
			outputStream = file(name+"p"+my_str+ext, "wb")
			output.write(outputStream)
			outputStream.close()
			j=j+1
		i=i+1
	print (str(i)+" pages processed")
###### end split ######

def select(args):
	operations = []
	outputfilename = args[-1]
	nr_of_files = 0
	for i in args[:-1]:
		if (re.match('.*?\.pdf', i)):
			nr_of_files = nr_of_files + 1
			operations.append({"name":i,"pages":[]})
		else:
			if (re.match('[0-9]+-[0-9]+', i)):
				(begin,sep,end) = i.partition("-")
				for j in range(int(begin), int(end)+1):
					operations[-1]["pages"].append(int(j))
			else:
				operations[-1]["pages"].append(int(i))
# 	print (str(operations)+"output: "+str(outputfilename))
# 	sys.exit(0)
	output = PdfFileWriter()
# 	try:
	for pdf in operations:
		print (pdf["name"])
		fiel = PdfFileReader(file(pdf["name"], "rb"))
		for pagenr in pdf["pages"]:
			if (not (pagenr > fiel.getNumPages()) and not(pagenr < 1)):
				output.addPage(fiel.getPage(pagenr-1))
			else:
				halp()
				print("one or more pages are not in the chosen PDF")
				sys.exit(3) #wrong pages or ranges
# 	except:
# 		halp()
# 		sys.exit(2) # pdf file is no pdf file...h
	if (not os.path.exists(outputfilename)):
		outputStream = file(outputfilename, "wb")
		output.write(outputStream)
		outputStream.close()
	else:
		print ("file exists, discontinuing operation")
###### end select ######

def delete(args):
	operations = []
	outputfilename = args[-1]
	nr_of_files = 0
	for i in args[:-1]:
		if (re.match('.*?\.pdf', i)):
			nr_of_files = nr_of_files + 1
			operations.append({"name":i,"pages":[]})
		else:
			if (re.match('[0-9]+-[0-9]+', i)):
				(begin,sep,end) = i.partition("-")
				for j in range(int(begin), int(end)+1):
					operations[-1]["pages"].append(int(j))
			else:
				operations[-1]["pages"].append(int(i))
# 	print (str(operations)+"output: "+str(outputfilename))
# 	sys.exit(0)
	output = PdfFileWriter()
# 	try:
	for pdf in operations:
		print (pdf["name"])
		fiel = PdfFileReader(file(pdf["name"], "rb"))
# 		for pagenr in pdf["pages"]:
		for pagenr in range(1,fiel.getNumPages()+1):
			if (pagenr not in pdf["pages"]):
				output.addPage(fiel.getPage(pagenr-1))
			else:
				print ("skipping page nr: "+str(pagenr))
# 	except:
# 		halp()
# 		sys.exit(2) # pdf file is no pdf file...h
	if (not os.path.exists(outputfilename)):
		outputStream = file(outputfilename, "wb")
		output.write(outputStream)
		outputStream.close()
	else:
		print ("file exists, discontinuing operation")
###### end delete ######


parse_args(sys.argv)

