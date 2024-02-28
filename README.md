# Directory_Scan

## Parameters
```bash
usage: python3 Directory_Scan.py [options]

Directory Scan

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --directory DIR
                        The target directory to be scanned;default: current working directory.
  -s INT, --split INT   The depth of the directory task split;[default: 5]
  -n INT, --number INT  Sort by file size, and enter the first 20 file information;[default: 20]
  -m INT, --maximum_depth INT
                        Only the maximum depth relative to the scanned directory is output;[default: 3]
  -w FILE, --whitelist FILE
                        Whitelist of directories/files, which does not count files or directories;[default: WhiteList.txt]
  -p INT, --process_num INT
                        Number of multi-process processes;[default: 4]
  -o DIR, --outdir DIR  The directory of the result output;default: current working directory.
```
## Output:
- DirectorySizeStatistics.xls
- Disk_Usage.User.tsv
- TheLargestTop.20.files.tsv
