# Ext2/3 superblock reader

This is simple util, which can parse ext2/3 filesystem superblock.

If you want to try, you can clone this repo:

```bash
$ git clone https://github.com/dokzlo13/ext_superblock.git
$ cd ext_superblock
```

or just download single util-file by "wget":

```bash
$ https://raw.githubusercontent.com/dokzlo13/ext_superblock/master/ext-superblock.py
```

Then, you can create superblock hexdump or detailed report. Specify work mode and path to file, formatted as ext2/3 filesystem:

```
$ python ./ext-superblock.py hexdump /dev/sda1
$ python ./ext-superblock.py analyze /dev/sda1
```

If you use real drives, possible "Permission denied" error may happen. Check your permissions, or run util with "sudo". Keep calm, it won't break your hard drives - all the code is in front of you :).

This repo also contains file "example/filesystem.ext3", which used in examples below.

<details>
  <summary>Output examples</summary>
  
    ```
    $ python ./ext-superblock.py -h                                                       
    usage: ext-superblock.py [-h] {hexdump,analyze} ...

    This is a script to analyze the superblock of an ext2/ext3 formatted file.

    Such a file can be created as follows:
        $ dd count=4096 if=/dev/zero of=filesystem.ext3
        $ mkfs.ext3 filesystem.ext3

    It can be mounted with :
        $ sudo mount -t ext3 -o loop filesystem.ext3 /mnt/mountpoint

    positional arguments:
    {hexdump,analyze}
        hexdump          Print hexdump of EXT superblock
        analyze          Read and parse EXT superblock

    optional arguments:
    -h, --help         show this help message and exit

    $ python ./ext-superblock.py analyze -h                              
    usage: ext-superblock.py analyze [-h] [-j] filename

    positional arguments:
    filename    Path to file with EXT filesystem

    optional arguments:
    -h, --help  show this help message and exit
    -j, --json  Output report as json

    $ python ./ext-superblock.py hexdump -h 
    usage: ext-superblock.py hexdump [-h] filename

    positional arguments:
    filename    Path to file with EXT filesystem

    optional arguments:
    -h, --help  show this help message and exit
    
    $ python ./ext-superblock.py hexdump ./example/filesystem.ext3       
                        HEX                       ASCII      
    1:  00010000 00080000 66000000 c1030000  b'........f.......'
    2:  f5000000 01000000 00000000 00000000  b'................'
    3:  00200000 00200000 00010000 00000000  b'. ... ..........'
    4:  1cad1a60 0000ffff 53ef0100 01000000  b'...`....S.......'
    5:  1cad1a60 00000000 00000000 01000000  b'...`............'
    6:  00000000 0b000000 80000000 3c000000  b'............<...'
    7:  02000000 03000000 b903e58a 8127460a  b".............'F."
    8:  b1f3880f 393f760f 00000000 00000000  b'....9?v.........'
    9:  00000000 00000000 00000000 00000000  b'................'
    10:  00000000 00000000 00000000 00000000  b'................'
    11:  00000000 00000000 00000000 00000000  b'................'
    12:  00000000 00000000 00000000 00000000  b'................'
    13:  00000000 00000000 00000000 00000700  b'................'
    14:  00000000 00000000 00000000 00000000  b'................'
    15:  08000000 00000000 00000000 611c408e  b'............a.@.'
    16:  f326454c afd46f8e 778879a5 01010000  b'.&EL..o.w.y.....'
    17:  0c000000 00000000 1cad1a60 3a000000  b'...........`:...'
    18:  3b000000 3c000000 3d000000 3e000000  b';...<...=...>...'
    19:  3f000000 40000000 41000000 42000000  b'?...@...A...B...'
    20:  43000000 44000000 45000000 46000000  b'C...D...E...F...'
    21:  47010000 00000000 00000000 00001000  b'G...............'
    22:  00000000 00000000 00000000 00000000  b'................'
    23:  01000000 00000000 00000000 00000000  b'................'
    24:  00000000 00000000 00000000 00000000  b'................'
    25:  00000000 00000000 00000000 00000000  b'................'
    26:  00000000 00000000 00000000 00000000  b'................'
    27:  00000000 00000000 00000000 00000000  b'................'
    28:  00000000 00000000 00000000 00000000  b'................'
    29:  00000000 00000000 00000000 00000000  b'................'
    30:  00000000 00000000 00000000 00000000  b'................'
    31:  00000000 00000000 00000000 00000000  b'................'
    32:  00000000 00000000 00000000 00000000  b'................'

    $ python ./ext-superblock.py analyze ./example/filesystem.ext3
    +-----+----------------------------------------+----------------------------------------+
    |  N  |                Field                   |                 Value                  |
    +-----+----------------------------------------+----------------------------------------+
    |  0  |         Total number of inodes         |                  256                   |
    +-----+----------------------------------------+----------------------------------------+
    |  1  |       Filesystem size in blocks        |                  2048                  |
    +-----+----------------------------------------+----------------------------------------+
    |  2  |       Number of reserved blocks        |                  102                   |
    +-----+----------------------------------------+----------------------------------------+
    |  3  |          Free blocks counter           |                  961                   |
    +-----+----------------------------------------+----------------------------------------+
    |  4  |          Free inodes counter           |                  245                   |
    +-----+----------------------------------------+----------------------------------------+
    |  5  |         Number of first block          |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    |  6  |              Block size:               |             0 (1024 Byte)              |
    +-----+----------------------------------------+----------------------------------------+
    |  7  |             Fragment size              |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    |  8  |        Number blocks per group         |                  8192                  |
    +-----+----------------------------------------+----------------------------------------+
    |  9  |       Number fragments per group       |                  8192                  |
    +-----+----------------------------------------+----------------------------------------+
    | 10  |        Number inodes per group         |                  256                   |
    +-----+----------------------------------------+----------------------------------------+
    | 11  |         Number of block groups         |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    | 12  |           Time of last mount           |        0 (1970-01-01 03:00:00)         |
    +-----+----------------------------------------+----------------------------------------+
    | 13  |           Time of last write           |    1612360988 (2021-02-03 17:03:08)    |
    +-----+----------------------------------------+----------------------------------------+
    | 14  |        Mount operations counter        |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 15  |     Number of mounts before check      |                 65535                  |
    +-----+----------------------------------------+----------------------------------------+
    | 16  |            Magic signature             |                 0XEF53                 |
    +-----+----------------------------------------+----------------------------------------+
    | 17  |              Status flag               |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    | 18  |     Behavior when detecting errors     |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    | 19  |          Minor revision level          |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 20  |           Time of last check           |    1612360988 (2021-02-03 17:03:08)    |
    +-----+----------------------------------------+----------------------------------------+
    | 21  |          Time between checks           |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 22  |         OS Filesystem created          |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 23  |             Revision level             |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    | 24  |  Default user ID for reserved blocks   |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 25  |  Default group ID for reserved blocks  |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 26  |     Number first nonreserved inode     |                   11                   |
    +-----+----------------------------------------+----------------------------------------+
    | 27  |    Size of on-disk inode structure     |                  128                   |
    +-----+----------------------------------------+----------------------------------------+
    | 28  |    Block group number of superblock    |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 29  |       Compatible features bitmap       |                 111100                 |
    +-----+----------------------------------------+----------------------------------------+
    | 30  |       Compatible features bitmap       |has_journal ext_attr resize_ino dir_index|
    +-----+----------------------------------------+----------------------------------------+
    | 31  |      Incompatible features bitmap      |            00010 (filetype)            |
    +-----+----------------------------------------+----------------------------------------+
    | 32  |       Read-only features bitmap        |     011 (sparse_super large_file)      |
    +-----+----------------------------------------+----------------------------------------+
    | 33  |     128-bit filesystem identifier      |  b903e58a-8127-460a-b1f3-880f393f760f  |
    +-----+----------------------------------------+----------------------------------------+
    | 34  |              Volume name               |                                        |
    +-----+----------------------------------------+----------------------------------------+
    | 35  |        Path of last mount point        |                                        |
    +-----+----------------------------------------+----------------------------------------+
    | 36  |         Compression Algorithm          |              00000 (none)              |
    +-----+----------------------------------------+----------------------------------------+
    | 37  |    Number of blocks to preallocate     |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 38  |Number of blocks to preallocate for dirs|                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 39  |              Journal UUID              |  00000000-0000-0000-0000-000000000000  |
    +-----+----------------------------------------+----------------------------------------+
    | 40  |          Journal inode number          |                   8                    |
    +-----+----------------------------------------+----------------------------------------+
    | 41  |         Journal device number          |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 42  |          Journal last orphan           |                   0                    |
    +-----+----------------------------------------+----------------------------------------+
    | 43  |               Hash seed                |               2386566241               |
    +-----+----------------------------------------+----------------------------------------+
    | 44  |               Hash seed                |               1279600371               |
    +-----+----------------------------------------+----------------------------------------+
    | 45  |               Hash seed                |               2389693615               |
    +-----+----------------------------------------+----------------------------------------+
    | 46  |               Hash seed                |               2776205431               |
    +-----+----------------------------------------+----------------------------------------+
    | 47  |              Hash version              |                   1                    |
    +-----+----------------------------------------+----------------------------------------+
    | 48  |         Default mount options          |         01100 (xattr_user acl)         |
    +-----+----------------------------------------+----------------------------------------+
    | 49  |       First meta block group ID        |                   0                    |
    +-----+----------------------------------------+----------------------------------------+

    $ python ./ext-superblock.py analyze ./example/filesystem.ext3 --json
    {
    "Total number of inodes": "256",
    "Filesystem size in blocks": "2048",
    "Number of reserved blocks": "102",
    "Free blocks counter": "961",
    "Free inodes counter": "245",
    "Number of first block": "1",
    "Block size:": "0 (1024 Byte)",
    "Fragment size": "0",
    "Number blocks per group": "8192",
    "Number fragments per group": "8192",
    "Number inodes per group": "256",
    "Number of block groups": "1",
    "Time of last mount": "0 (1970-01-01 03:00:00)",
    "Time of last write": "1612360988 (2021-02-03 17:03:08)",
    "Mount operations counter": "0",
    "Number of mounts before check": "65535",
    "Magic signature": "0XEF53",
    "Status flag": "1",
    "Behavior when detecting errors": "1",
    "Minor revision level": "0",
    "Time of last check": "1612360988 (2021-02-03 17:03:08)",
    "Time between checks": "0",
    "OS Filesystem created": "0",
    "Revision level": "1",
    "Default user ID for reserved blocks": "0",
    "Default group ID for reserved blocks": "0",
    "Number first nonreserved inode": "11",
    "Size of on-disk inode structure": "128",
    "Block group number of superblock": "0",
    "Compatible features bitmap": "has_journal ext_attr resize_ino dir_index",
    "Incompatible features bitmap": "00010 (filetype)",
    "Read-only features bitmap": "011 (sparse_super large_file)",
    "128-bit filesystem identifier": "b903e58a-8127-460a-b1f3-880f393f760f",
    "Volume name": "",
    "Path of last mount point": "",
    "Compression Algorithm": "00000 (none)",
    "Number of blocks to preallocate": "0",
    "Number of blocks to preallocate for dirs": "0",
    "Journal UUID": "00000000-0000-0000-0000-000000000000",
    "Journal inode number": "8",
    "Journal device number": "0",
    "Journal last orphan": "0",
    "Hash seed": "2776205431",
    "Hash version": "1",
    "Default mount options": "01100 (xattr_user acl)",
    "First meta block group ID": "0"
    }
    ```
  
</details>
