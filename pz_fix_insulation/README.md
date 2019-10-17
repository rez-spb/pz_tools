# `pz_fix_insulation`
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
## Summary
Set insulation for those items that lack the property to `1.0`.  
Used for build `41.12` as no insulation is implemented yet.

## Description
Pretty simple thing.  
Developers forgot to add proper insulation to all clothing items, 
so characters are prone to freezing to death in any vanilla clothes 
as the game thinks that no parameter equals zero.  
This script adds `'Insulation = 1.0'` to every clothing item it finds 
in files under `'$PZ_INSTALL_DIR'/media/scripts/clothing/` directory.

## Usability notes
* Use double quoted in `--directory` argument for paths with spaces;
* Does not touch items that already have insulation set.

## Arguments
```
usage: fix_insulation.py [-h] -d PATH [-v | -q]

Set insulation to 1.0 for clothing that lacks insulation.
For version 41.12.

optional arguments:
  -h, --help            show this help message and exit
  -d PATH, --directory PATH
                        path to Zomboid installation
  -v, --verbose         verbose output
  -q, --quiet           display warnings and errors only

v0.0.1 (2019-10-17) by rez_spb
```