#!/usr/bin/env python3

import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path


def interleave_pdfs(filename1, filename2, out_path=None, merge_name=None, reverse2=False):
    assert os.path.isfile(filename1)
    assert os.path.isfile(filename2)
    assert os.path.splitext(filename1)[1].lower() == '.pdf'
    assert os.path.splitext(filename2)[1].lower() == '.pdf'
    name1 = os.path.splitext(os.path.basename(filename1))[0]
    name2 = os.path.splitext(os.path.basename(filename2))[0]

    if out_path is None:
        out_path = os.path.dirname(filename1)
    if merge_name is None:
        merge_name = name1 + '_interleaved_' + name2

    outputPdf = PdfWriter()
    with open(filename1, 'rb') as infile1:
        with open(filename2, 'rb') as infile2:
            inputPdf1 = PdfReader(infile1)
            inputPdf2 = PdfReader(infile2)
            n1 = len(inputPdf1.pages)
            n2 = len(inputPdf2.pages)
            assert n1 == n2
            for i in range(n1):
                outputPdf.add_page(inputPdf1.pages[i])
                if reverse2:
                    outputPdf.add_page(inputPdf2.pages[n2-1-i])
                else:
                    outputPdf.add_page(inputPdf2.pages[i])
            with open(os.path.join(out_path, merge_name + '.pdf'), 'wb') as f:
                outputPdf.write(f)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        filename1 = sys.argv[1]
        filename2 = sys.argv[2]
        interleave_pdfs(filename1, filename2)
    elif len(sys.argv) == 1:
        ROOT_PATH = Path.home() / "Documents/SOS"
        raw_scans = ROOT_PATH / "01_raw_scans"
        merged_scans = ROOT_PATH / "02_merged_scans"
        for fname_front in raw_scans.glob("*_f.pdf"):
            base_name = fname_front.name.replace("_f.pdf", "")
            fname_back = fname_front.parent / (base_name + "_b.pdf")
            assert fname_back.exists()
            if (merged_scans / (base_name + ".pdf")).exists():
                continue
            interleave_pdfs(str(fname_front), str(fname_back), out_path=merged_scans, merge_name=base_name, reverse2=True)
    else:
        raise ValueError(len(sys.argv))
