Stapler
=======

Stapler is a pure Python alternative to [PDFtk][pdftk], a tool for manipulating
PDF documents from the command line.

[pdftk]: http://www.pdfhacks.com/pdftk/

History
-------
PDFtk was written in Java and C++, and
is natively compiled with gcj. Sadly, it has been discontinued a few years ago
and bitrot is setting in (e.g., it does not compile easily on a number of
platforms).

Philip Stark decided to look for an alternative and found pypdf, a PDF library
written in pure Python. He couldn't find a tool which actually used the
library, so he started writing his own.

This version of stapler is Fred Wenzel's fork of the project, with a completely
refactored source code, tests, and added functionality.

Like pdftk, stapler is a command-line tool. If you would like to add a GUI,
compile it into a binary for your favorite platform, or contribute anything else,
feel free to fork and send me a pull request.

License
-------
Stapler version 0.2 was written in 2009 by Philip Stark.
Stapler version 0.3 was written in 2010 by Fred Wenzel.

For a list of contributors, check the ``CONTRIBUTORS`` file.

Stapler is distributed under a BSD license. A copy of the BSD Style 
License used can be found in the file ``LICENSE``.

Usage
-----
There are 4 modes in Stapler:

### cat
Works like the normal unix utility "cat", meaning it con<em>cat</em>enates
files.

The syntax is delightfully simple:

    stapler cat input1 [input2, input3, ...] output
    # example:
    stapler cat a.pdf b.pdf c.pdf output.pdf
    # this would append "b.pdf" and "c.pdf" to "a.pdf" and write the whole
    # thing to "output.pdf"

You can specify as many input files as you want, it always cats all but the
last file specified and writes the whole thing into the last file specified.

### split:
Splits the specified pdf files into their single pages and writes each page
into it's own pdf file with this naming scheme:

    ${origname}p${zeropaddedpagenr}.pdf

Syntax:

    stapler split input1 [input2 input3 ...]

Example for a file foobar.pdf with 20 pages:

    $ stapler split foobar.pdf
    $ ls
        foobarp01.pdf foobarp02.pdf ... foobarp19.pdf foobarp20.pdf

Multiple files can be specified, they will be processed as if you called
single instances of stapler.

### select/delete (called with ``sel`` and ``del``, respectively)
These are the most sophisticated modes. With select, you can cherry-pick pages
out of pdfs and concatenate them into a new pdf file.

Syntax:

    stapler sel input1 page_or_range [page_or_range ...] [input2 p_o_r ...]

Example:

    stapler sel a.pdf 1 4-8 20-40 b.pdf 1-5 output.pdf
    # this generates a pdf called output.pdf with the following pages:
    # 1, 4-8, 20-40 from a.pdf, 1-5 from b.pdf in this order

What you _cannot_ do yet is _not_ specifying any ranges. I will probably merge
select and cat so that you can specify pages and ranges, but if you don't,
it just uses the whole file.

The delete command works almost exactly the same as select, but inverse.
It cherry-picks the pages and ranges which you _didn't_ specify out of the
pdfs.
