#!/usr/bin/env bash

./automatically_rename_raw_scans_from_today.py
./interleavePdfPages.py
./apply_ocr2scans.bash
./app.py ~/Documents/SOS/03_ocr_scans
