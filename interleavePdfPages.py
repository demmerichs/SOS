#!/usr/bin/env python3

import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter


if __name__ == '__main__':
    assert(len(sys.argv) == 3)
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    assert(os.path.isfile(filename1))
    assert(os.path.isfile(filename2))
    assert(os.path.splitext(filename1)[1].lower() == '.pdf')
    assert(os.path.splitext(filename2)[1].lower() == '.pdf')
    dir = os.path.dirname(filename1)
    name1 = os.path.splitext(os.path.basename(filename1))[0]
    name2 = os.path.splitext(os.path.basename(filename2))[0]

    outputPdf = PdfFileWriter()
    with open(filename1, 'rb') as infile1:
        with open(filename2, 'rb') as infile2:
            inputPdf1 = PdfFileReader(infile1)
            inputPdf2 = PdfFileReader(infile2)
            assert(inputPdf1.getNumPages() == inputPdf2.getNumPages())
            for i in range(inputPdf1.getNumPages()):
                outputPdf.addPage(inputPdf1.getPage(i))
                outputPdf.addPage(inputPdf2.getPage(i))
            with open(os.path.join(dir, name1+'_interleaved_'+name2+'.pdf'), 'wb') as f:
                outputPdf.write(f)
