#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from PyPDF2.pdf import PdfFileReader

from staplelib import main, CommandError

HERE = os.path.abspath(os.path.dirname(__file__))
TESTFILE_DIR = os.path.join(HERE, 'testfiles')
STAPLER = os.path.join(HERE, '..', 'stapler')
ONEPAGE_PDF = os.path.join(TESTFILE_DIR, '1page.pdf')
FIVEPAGE_PDF = os.path.join(TESTFILE_DIR, '5page.pdf')


def run_stapler(arguments):
    main(arguments)


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
        run_stapler(['cat', ONEPAGE_PDF, FIVEPAGE_PDF,
                     self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 6)

    def test_sel_one_page(self):
        """Test select of a one page from a PDF file."""
        run_stapler(['sel', 'A=' + FIVEPAGE_PDF, 'A2', self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 1)

    def test_sel_range(self):
        """Test select of more pages from a PDF file."""
        run_stapler(['cat', 'A=' + FIVEPAGE_PDF, 'A2-4', self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 3)

    def test_del_one_page(self):
        """Test del command for inverse select of one page."""
        run_stapler(['del', 'A=' + FIVEPAGE_PDF, 'A1', self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 4)

    def test_del_range(self):
        """Test del command for inverse select multiple pages."""
        run_stapler(['del', 'A=' + FIVEPAGE_PDF, 'A2-4', self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 2)

    def test_split(self):
        """Make sure a file is properly split into pages."""
        run_stapler(['split', FIVEPAGE_PDF])

        filelist = os.listdir(self.tmpdir)
        self.assertEqual(len(filelist), 5)
        for f in os.listdir(self.tmpdir):
            with open(os.path.join(self.tmpdir, f), 'rb') as pdf_file:
                pdf = PdfFileReader(pdf_file)
                self.assertEqual(pdf.getNumPages(), 1)

    def test_zip(self):
        """Test zip."""
        run_stapler(['zip', ONEPAGE_PDF, FIVEPAGE_PDF, self.outputfile])
        self.assertTrue(os.path.isfile(self.outputfile))
        with open(self.outputfile, 'rb') as outputfile:
            pdf = PdfFileReader(outputfile)
            self.assertEqual(pdf.getNumPages(), 6)

    def test_output_file_already_exists(self):
        """Test zip."""
        with self.assertRaises(SystemExit) as e:
            run_stapler(['zip', ONEPAGE_PDF, FIVEPAGE_PDF])
        self.assertEqual(e.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
