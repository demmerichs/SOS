#!/usr/bin/env python3

from pathlib import Path
import datetime as dt

def rename_scans(directory):
    files = list(directory.glob("*.pdf"))
    files = sorted(files, key=lambda x: x.stat().st_mtime)
    start_today = dt.datetime.combine(dt.date.today(), dt.time(hour=3))
    files = list(filter(
        lambda x: dt.datetime.fromtimestamp(x.stat().st_mtime) > start_today,
        files,
    ))

    today_str = dt.date.today().strftime("%Y%m%d")
    for i in range(len(files)):
        if i%2 == 0:
            new_name = "%s_%02d_f" % (today_str, 1+i//2)
        else:
            new_name = "%s_%02d_b" % (today_str, 1+i//2)

        fname = files[i]
        target = fname.parent / (new_name + fname.suffix)

        if target == fname:
            continue
        if target.exists():
            raise ValueError("target exists: %s" % target)
        fname.rename(target)


if __name__ == '__main__':
    rename_scans(Path.home() / "Documents/SOS/01_raw_scans")
