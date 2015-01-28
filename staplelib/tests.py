#!/usr/bin/env python

import os.path
import shutil
from subprocess import check_call
import tempfile
import unittest

from PyPDF2 import PdfFileReader


HERE = os.path.abspath(os.path.dirname(__file__))
TESTFILE_DIR = os.path.join(HERE, 'testfiles')
STAPLER = os.path.join(HERE, '..', 'stapler')
ONEPAGE_PDF = os.path.join(TESTFILE_DIR, '1page.pdf')
FIVEPAGE_PDF = os.path.join(TESTFILE_DIR, '5page.pdf')


class TestStapler(unittest.TestCase):
    """Some unit tests for the stapler tool."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.outputfile = os.path.join(self.tmpdir, 'output.pdf')
        os.chdir(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        os.chdir(HERE)

    def test_cat(self):
        """Make sure files are properly concatenated."""
        check_call([STAPLER, 'cat', ONEPAGE_PDF, FIVEPAGE_PDF,
                    self.outputfile])
        self.assert_(os.path.isfile(self.outputfile))
        pdf = PdfFileReader(file(self.outputfile, 'rb'))
        self.assertEqual(pdf.getNumPages(), 6)

    def test_split(self):
        """Make sure a file is properly split into pages."""
        check_call([STAPLER, 'split', FIVEPAGE_PDF])

        filelist = os.listdir(self.tmpdir)
        self.assertEqual(len(filelist), 5)
        for f in os.listdir(self.tmpdir):
            pdf = PdfFileReader(file(os.path.join(self.tmpdir, f), 'rb'))
            self.assertEqual(pdf.getNumPages(), 1)


if __name__ == '__main__':
    unittest.main()
