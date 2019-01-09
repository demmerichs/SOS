# SOS
Sorting Out Scans (SOS): A tool that processes multiples scanned document pages and provides a clean and fast interface for sorting them away manually in a fast and efficient way.


## Processing steps

### 1. Scanning
This is simple. Use your scanner and have large pdf files. 300 dpi is fine.

### 2. Ordering
If you scanned in a batched way the front pages and afterwards the back pages, they are probably in reverse order, so first reverse the order of the back pages and then interleave the front with the back pages. Two scripts for these tasks can be found in this repo.

### 3. Deleting and rotating
Use a native application for rotating (by 90, 180, 270 degrees) the pages and deleting empty/useless pages. A suggestion for Linux would be `pdf-shuffler`.

### 4. Perform OCR
Use `ocrmypdf` command line tool on Linux. A script for applying it to all pdf files in a folder can be found inside this repo.

### 5. Sort away Scans (SOS)
Use the app in this repo to iterate in a fast and efficient, yet manual way, over the pdf files to sort away the single pdf pages into directories and/or appending them to existing documents. More information about this tool will be provided in the beginning of this README.

## TODOs
- [x] include correct languages for the ocr step (german and english)
- [x] use the ocr text in the last step instead of reprocessing the image again
- [ ] add more SOS specific information at the beginning of this README
- [x] watermark processed pages
- [ ] create script managing all 5 steps in one go
- [x] use dates and page up page down keys in filename creation
