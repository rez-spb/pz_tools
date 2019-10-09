# pz_save_vacuum
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
## Summary
Remove old files from Project Zomboid multiplayer saves to cut sizes.

## Description
This script is mostly useful to people who like to make automated backups of
their save data in case of corruption (that's a frequent thing in PZ).
Most people backup only their `'map_p.bin'` file, which, while being most space
efficient, can lead to falling from the sky and instantly dying characters.
To fight this unwanted behaviour I preserve data chunks that were present when
character disconnected and some time before that.

Script helps to clean older chunks which are mostly remote and prone to change
on the server, so not much point in storing them locally. However it preserves
chunks for last `X` days you specify regardless of how remote they are from your
character.

## Usability notes
* Won't ever delete `'map_p.bin'` file;
* Won't accept `--days` value less than 1;
* The most time consuming operation is getting each file size, which can stretch
for minutes for huge save directories, so there's a `'--faster'` option that
bypasses size measuring;
* Has `--dry-run` argument for those who aren't easily persuaded to run anything 
that removes files without testing it first;
* Should autodetect saves directory correctly, but not tested on a Mac.

## Arguments
```
usage: save_vacuum.py [-h] -d INT [-f] [--dry-run] [-v | -q]

Remove files older than X days from Project Zomboid multiplayer saves directory
with map_p.bin being an exception.
Local server directories are not affected.

optional arguments:
  -h, --help          show this help message and exit
  -d INT, --days INT  days to preserve in save (1 or more)
  -f, --faster        do not count freed size to speed things up
  --dry-run           do not perform actual removal, just count files
  -v, --verbose       verbose output
  -q, --quiet         display warnings and errors only

v0.1.0 (2019-10-09) by rez_spb
```