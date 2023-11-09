#!/usr/bin/env bash

./interleavePdfPages.py
./apply_ocr2scans.bash
./app.py ~/Documents/SOS/03_ocr_scans
