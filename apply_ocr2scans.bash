#!/usr/bin/env bash

OCRCMD="ocrmypdf -l deu+eng --rotate-pages --deskew --clean -v1 --optimize 1"

ROOTDIR=~/Documents/SOS

for f in $ROOTDIR/02_merged_scans/*.pdf
do
    filename=$(basename -- "$f")
    $OCRCMD $f $ROOTDIR/03_ocr_scans/$filename
done
