#!/usr/bin/env bash

if [ ! -z $1 ]
then
    cd $1
fi

if [ -d "ocr" ]
then
    i=1
    while [ -d "ocr"$i ]
    do
        i=$((i+1))
    done
    mkdir "ocr"$i
    ocrdir="ocr"$i
else
    mkdir ocr
    ocrdir="ocr"
fi

for f in *.pdf
do
    filename=$(basename -- "$f")
    filename="${filename%.*}"
    dir=$(dirname $f)
    ocrmypdf -l deu -l eng $f $dir/$ocrdir/$filename"_ocr.pdf"
done

for f in *.PDF
do
    filename=$(basename -- "$f")
    filename="${filename%.*}"
    dir=$(dirname $f)
    ocrmypdf -l deu -l eng $f $dir/$ocrdir/$filename"_ocr.pdf"
done
