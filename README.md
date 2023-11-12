# SOS
Sorting Out Scans (SOS): A tool that processes multiples scanned document pages and provides a clean and fast interface for sorting them away manually in a fast and efficient way.

## Hotkeys
| Key | Action | Note |
|------|------|------|
| Del  | ignore current pdf page  | accidental usage for changing text field  |
| Enter (.pdf ending) | save pdf under current text entry  | |
| Enter (non-.pdf ending) | append to last entered pdf | not tested yet |
| Page-UpDown  | Cycle through dates detected  |  |
| Arrow UpDown  | Cycle through history  |  |
| Alt+Backspace  | go folder up in text field  | not yet tested |
| Tab | autocomplete to first hit | |

## Folder layout
use `make_scan_folders.bash` or `setup.sh` which calls this creation script. It creates the following directories in the user space:
```
~/Documents/SOS/01_raw_scans
~/Documents/SOS/02_merged_scans
~/Documents/SOS/03_ocr_scans
```

## Processing steps

### 1. Scanning
This is simple. Use your scanner and have large pdf files. 300 dpi is fine.
If you scan both sides, make sure just to flip your pile of paper, and put both pdf documents in `01_raw_scans`. The page order should be `1, 3, 5, ..., 2n-1` in the first scan, and `2n, 2n-2, ..., 6, 4, 2` in the second.
If you scan only the front, put it directly into `02_merged_scans`.
The following steps can be done manually, or just call `./run_SOS.bash` to perform them in one go.

### 2. Ordering
If you scanned in a batched way the front pages and afterwards the back pages, they are probably in reverse order, so first reverse the order of the back pages and then interleave the front with the back pages.
You can just run `./automatically_rename_raw_scans_from_today.py; ./interleavePdfPages.py`, which will first rename scans in `01_raw_scans`, and then produce merged scans in `02_merged_scans`.
These two steps are part of `run_SOS.bash`.

### 3. Perform OCR
Use `./apply_ocr2scans.bash` to apply optical character recognition and deskewing for the scans in `02_merged_scans` and place the modified pdfs in `03_ocr_scans`.
This step is part of `run_SOS.bash`.

### 5. Sort away Scans (SOS)
Use the app in this repo to iterate in a fast and efficient, yet manual way, over the pdf files to sort away the single pdf pages into directories and/or appending them to existing documents. More information about this tool will be provided in the beginning of this README.
This final step is also automatically called for all pdfs in `03_ocr_scans` through `run_SOS.bash`.

## TODOs
- [x] include correct languages for the ocr step (german and english)
- [x] use the ocr text in the last step instead of reprocessing the image again
- [ ] add more SOS specific information at the beginning of this README
- [ ] add hotkey table with columns for further additions and also bad current hotkeys
- [ ] do pdf page operations in extra process in order for main user process not to wait for page appending process to finish (especially slow on remote file servers eg GDrive)
- [ ] detect xx.xx.xx date as year 20xx (dynamically do the 20 based on current date ;) to be extra safe)
- [x] watermark processed pages
- [x] create script managing all 5 steps in one go
- [x] use dates and page up page down keys in filename creation
