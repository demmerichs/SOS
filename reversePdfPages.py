#!/usr/bin/env python3

import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter


if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    filename = sys.argv[1]
    assert(os.path.isfile(filename))
    assert(os.path.splitext(filename)[1].lower() == '.pdf')
    dir = os.path.dirname(filename)
    name = os.path.splitext(os.path.basename(filename))[0]

    outputPdf = PdfFileWriter()
    with open(filename, 'rb') as infile:
        inputPdf = PdfFileReader(infile)
        for i in range(inputPdf.getNumPages()-1, -1, -1):
            outputPdf.addPage(inputPdf.getPage(i))
        with open(os.path.join(dir, name+'_reversed.pdf'), 'wb') as f:
            outputPdf.write(f)
