#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Philip Stark
# the license is found in the file "LICENSE"
# if this file is missing, you can find a copy at
# http://stuff.codechaos.ch/stapler_license

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
		halp()
		sys.exit(0)
	
	if argv[1] == "-h":
		halp()
		sys.exit(0)
	
	mode = argv[1]
	files = argv[2:]
	if (mode in modes):
		print "mode: "+mode
	else:
		print "please input a valid mode"
		halp()
		sys.exit()

	if (mode == "cat"):
		cat(files[:-1],files[-1], True)
	elif (mode == "split"):
		split(files, True)
	else:
		operations = []
		for inputname in files[:-1]:
			if (re.match('.*?\.pdf', inputname)):
				operations.append({"name":inputname,"pages":[]})
			else:
				if (re.match('[0-9]+-[0-9]+', inputname)):
					(begin,sep,end) = inputname.partition("-")
					for j in range(int(begin), int(end)+1):
						operations[-1]["pages"].append(int(j))
				else:
					operations[-1]["pages"].append(int(inputname))
	if (mode == "del"):
		delete(operations, files[-1], True)
	elif (mode == "sel"):
		select(operations, files[-1], True)
###### end function parse_args ######

def halp():
	print ("""Usage: stapler mode arguments [output]
	arguments:
		cat: input pdf files (output is needed for this mode)
		split: input pdf files (no output needed)
		sel: <inputfile> <pagenr>|<pagerange> ... (output needed)
		del: <inputfile> <pagenr>|<pagerange> ... (output needed)""")
###### end function halp ######

def cat(infilenames, outputfilename, verbose):
	inputs = []
	for infilename in infilenames:
		print infilename
		if not os.path.exists(infilename):
			halp()
			print ("error: "+infilename+" does not exist... exiting nao")
			sys.exit(2) # pdf file is no pdf file...
	if os.path.exists(outputfilename):
		halp()
		print ("error: "+outputfilename+" does already exist... exiting nao")
		sys.exit(2) # pdf file is no pdf file...
	try: 
		for i in infilenames:
			inputs.append(PdfFileReader(file(i, "rb")))
	except:
		halp()
		sys.exit(2) # pdf file is no pdf file...
	
	i = 0
	output = PdfFileWriter()

	for pdf in inputs:
		for pagenr in range(pdf.getNumPages()):
			output.addPage(pdf.getPage(pagenr))
			i=i+1
	outputStream = file(outputfilename, "wb")
	output.write(outputStream)
	outputStream.close()
	if verbose: print (str(i)+" pages processed")
###### end function cat ######

def split(files, verbose):

	for infilename in files:
		if not os.path.exists(infilename):
			halp()
			print ("error: "+infilename+" does not exist... exiting nao")
			sys.exit(2) # pdf file is no pdf file...
	inputs = []
	try:
		for i in files:
			inputs.append(PdfFileReader(file(i, "rb")))
	except:
		halp()
		print ("there has been an error of unfortunate proportions")
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
	if verbose: print (str(j)+" pages in "+str(i)+" files processed")
###### end function split ######

def select(filesandranges, outputfilename, verbose):

 	if verbose: print (str(filesandranges)+"\noutput: "+str(outputfilename))

	for i in range(len(filesandranges)):
		if not os.path.exists(filesandranges[i]['name']):
			halp()
			print ("error: "+filesandranges[i]['name']+" does not exist... exiting nao")
			sys.exit(2) # pdf file is no pdf file...
	if os.path.exists(outputfilename):
		halp()
		print ("error: "+filesandranges[i]['name']+" does already exist... exiting nao")
		sys.exit(2) # pdf file is no pdf file...

	output = PdfFileWriter()
 	try:
		for pdf in filesandranges:
			fiel = PdfFileReader(file(pdf["name"], "rb"))
			for pagenr in pdf["pages"]:
				if (not (pagenr > fiel.getNumPages()) and not(pagenr < 1)):
					output.addPage(fiel.getPage(pagenr-1))
				else:
					print("one or more pages are not in the chosen PDF")
					halp()
					sys.exit(3) #wrong pages or ranges
 	except:
 		halp()
 		sys.exit(2) # pdf file is no pdf file...h
	if (not os.path.exists(outputfilename)):
		outputStream = file(outputfilename, "wb")
		output.write(outputStream)
		outputStream.close()
	else:
		print ("file exists, discontinuing operation")
###### end function select ######

def delete(filesandranges, outputfilename, verbose):

	for i in range(len(filesandranges)):
		if not os.path.exists(filesandranges[i]['name']):
			halp()
			print ("error: "+filesandranges[i]['name']+" does not exist... exiting nao")
			sys.exit(2) # pdf file is no pdf file...
	if os.path.exists(outputfilename):
		halp()
		print ("error: "+filesandranges[i]['name']+" does already exist... exiting nao")
		sys.exit(2) # pdf file is no pdf file...

	output = PdfFileWriter()
 	try:
		for pdf in filesandranges:
			print (pdf["name"])
			fiel = PdfFileReader(file(pdf["name"], "rb"))

			for pagenr in range(1,fiel.getNumPages()+1):
				if (pagenr not in pdf["pages"]):
					output.addPage(fiel.getPage(pagenr-1))
#				else:
#					print ("skipping page nr: "+str(pagenr))
	except:
 		halp()
 		sys.exit(2) # pdf file is no pdf file...
	if (not os.path.exists(outputfilename)):
		outputStream = file(outputfilename, "wb")
		output.write(outputStream)
		outputStream.close()
	else:
		print ("file exists, discontinuing operation")
###### end function delete ######


parse_args(sys.argv)

