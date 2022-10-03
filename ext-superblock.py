#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import string
import sys
from binascii import hexlify
from datetime import datetime

__copyright__ = "Copyright 2022"
__author__ = "Alex Zakharov <dokzlo13@gmail.com>"
__credits__ = ["Alex Zakharov"]
__email__ = "alex@zloy.name"
__license__ = "MIT"
__version__ = "1.0.0"


BLOCKSIZE = 512

if sys.version_info >= (3, 0):
    _unicode = lambda x: str(x)
    _range = range

    def join(data, separator=" "):
        separator = separator.encode("utf-8") if not isinstance(separator, bytes) else separator
        clear = []
        for chunk in data:
            if isinstance(chunk, bytes):
                clear.append(chunk)
            elif isinstance(chunk, int):
                clear.append(bytes([chunk]))
            elif isinstance(chunk, str):
                clear.append(chunk.encode("utf-8"))

        return separator.join(clear)

    def lsb2ascii(b_string):
        return b_string.rstrip(b"\x00").decode("utf-8")

    def nonprintable_replace(char):
        if char not in string.printable.encode("utf-8"):
            return b"."
        if char in b"\n\r\t\x0b\x0c":
            return b"."
        return char

elif sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding("utf8")
    _unicode = unicode
    _range = xrange
    split_literal = b"\0"

    def join(data, separator=""):
        return separator.join(data)

    def nonprintable_replace(char):
        if char not in string.printable:
            return "."
        if char in "\n\r\t\x0b\x0c":
            return "."
        return char

    def lsb2ascii(b_string):
        """Take a binary string (from ``file.read()``) and convert it to an
        ascii string."""
        msb_string = hexlify(b_string)
        pairs = (msb_string[x : x + 2] for x in range(0, len(msb_string), 2))
        values = (int(x, 16) for x in pairs)
        return join(map(chr, values))

else:
    print("Unsupported python version: '{}'".format(sys.version))
    sys.exit(1)


class ExtSuperblockReport:
    def __init__(self):
        self.report = []

    def record(self, field, value):
        self.report.append((field, value))

    def __str__(self):
        out = ""
        out += (
            "+-----+----------------------------------------+----------------------------------------+\n"
            "|  N  |                Field                   |                 Value                  |\n"
            "+-----+----------------------------------------+----------------------------------------+\n"
        )
        for idx, (field, value) in enumerate(self.report):
            out += "|{index:^5}|{field:^40}|{value:^40}|\n".format(index=idx, field=field, value=value)
            out += "+" + "-" * 5 + "+" + "-" * 40 + "+" + "-" * 40 + "+\n"
        return out

    def as_dict(self):
        return dict(self.report)


class ExtSuperblock:
    # Binary conversion functions
    lsb2ascii = lsb2ascii

    @staticmethod
    def lsb2hex(b_string):
        """Take a binary string (from ``file.read()``) and convert it into a
        hex string by assuming 2 byte little endian byte order."""
        msb_string = hexlify(b_string)
        lsb_string = join([msb_string[x : x + 2] for x in range(0, len(msb_string), 2)][::-1], "")
        return lsb_string

    @staticmethod
    def lsb2int(b_string):
        """Take a binary string (from ``file.read()``) and convert it into a
        integer by assuming 2 byte little endian byte order."""
        lsb_string = ExtSuperblock.lsb2hex(b_string)
        return int(lsb_string, 16)

    # Formatting functions

    @staticmethod
    def uuid(h_string):
        """Format a hex string like an UUID."""
        split = lambda x: [x[:8], x[8:12], x[12:16], x[16:20], x[20:]]
        return join(split(h_string), "-").decode("utf-8")

    @staticmethod
    def timestamp(seconds):
        return datetime.fromtimestamp(seconds)

    @staticmethod
    def map_bitmap(value, mapping):
        """Map a bitmap to the corresponding human readable strings."""
        return " ".join([t[1] for t in mapping if value & t[0]]) or "none"

    def __init__(self, fp) -> None:
        self.fp = fp
        if not self.check_is_ext(fp):
            raise Exception("File doesn't contains EXT superblock")

    def hexdump(self):
        f = self.fp
        f.seek(0)
        f.seek(2 * BLOCKSIZE)
        out = ""
        out += " " * 5 + "HEX".center(35) + "  " + "ASCII".center(16) + "\n"
        for i in _range(BLOCKSIZE // 16):
            row = f.read(4), f.read(4), f.read(4), f.read(4)
            hex_string = join(map(hexlify, row), " ").decode("utf-8")
            ascii_string = join(map(nonprintable_replace, join(row, b"")), b"")
            out += "{0:2}:  {1}  {2}\n".format(i + 1, hex_string, ascii_string)
        out += "\n"
        return out

    def analyze(self):
        report = ExtSuperblockReport()
        f = self.fp
        f.seek(0)

        def record(field, value):
            report.record(field, value)

        # EXT2/3 Block layout gathered from:
        # - https://flylib.com/books/en/2.48.1/superblock.html
        # - https://www.nongnu.org/ext2-doc/ext2.html#superblock
        # Not implemented EXT4 layout can be found here:
        # - https://ext4.wiki.kernel.org/index.php/Ext4_Disk_Layout#The_Super_Block

        f.seek(2 * BLOCKSIZE)
        # Bytes 0-15
        inodes_total = self.lsb2int(f.read(4))
        record("Total number of inodes", "{0:d}".format(inodes_total))
        record("Filesystem size in blocks", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Number of reserved blocks", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Free blocks counter", "{0:d}".format(self.lsb2int(f.read(4))))

        # Bytes 16-31
        record("Free inodes counter", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Number of first block", "{0:d}".format(self.lsb2int(f.read(4))))
        val = self.lsb2int(f.read(4))
        record("Block size:", "{0:d} ({1:d} Byte)".format(val, 1024 * 2**val))
        record("Fragment size", "{0:d}".format(self.lsb2int(f.read(4))))

        # Bytes 32-47
        record("Number blocks per group", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Number fragments per group", "{0:d}".format(self.lsb2int(f.read(4))))
        inodes_per_group = self.lsb2int(f.read(4))
        record("Number inodes per group", "{0:d}".format(inodes_per_group))
        record("Number of block groups", "{0:d}".format(inodes_total // inodes_per_group))
        mtime = self.lsb2int(f.read(4))
        record("Time of last mount", "{0:d} ({1:%Y-%m-%d %H:%M:%S})".format(mtime, self.timestamp(mtime)))

        # Bytes 48-63
        wtime = self.lsb2int(f.read(4))
        record("Time of last write", "{0:d} ({1:%Y-%m-%d %H:%M:%S})".format(wtime, self.timestamp(wtime)))
        record("Mount operations counter", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Number of mounts before check", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Magic signature", "{0:#X}".format(self.lsb2int(f.read(2))))
        record("Status flag", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Behavior when detecting errors", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Minor revision level", "{0:d}".format(self.lsb2int(f.read(2))))

        # Bytes 64-79
        last_check = self.lsb2int(f.read(4))
        record("Time of last check", "{0} ({1:%Y-%m-%d %H:%M:%S})".format(last_check, self.timestamp(last_check)))
        check_interval = self.lsb2int(f.read(4))
        record("Time between checks", "{0:d}".format(check_interval))
        record("OS Filesystem created", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Revision level", "{0:d}".format(self.lsb2int(f.read(4))))

        # Bytes 80-95
        record("Default user ID for reserved blocks", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Default group ID for reserved blocks", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Number first nonreserved inode", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Size of on-disk inode structure", "{0:d}".format(self.lsb2int(f.read(2))))
        record("Block group number of superblock", "{0:d}".format(self.lsb2int(f.read(2))))
        feature_compat = self.lsb2int(f.read(4))
        feature_compat_s = self.map_bitmap(
            feature_compat,
            (
                (0b000001, "dir_prealloc"),
                (0b000010, "imagic_inodes"),
                (0b000100, "has_journal"),
                (0b001000, "ext_attr"),
                (0b010000, "resize_ino"),
                (0b100000, "dir_index"),
            ),
        )
        record("Compatible features bitmap", "{0:06b}".format(feature_compat))
        record("Compatible features bitmap", "{0}".format(feature_compat_s))

        # Bytes 96-103
        feature_incompat = self.lsb2int(f.read(4))
        feature_incompat_s = self.map_bitmap(
            feature_incompat,
            (
                (0b00001, "compression"),
                (0b00010, "filetype"),
                (0b00100, "recover"),
                (0b01000, "journal_dev"),
                (0b10000, "meta_bg"),
            ),
        )
        record("Incompatible features bitmap", "{0:05b} ({1})".format(feature_incompat, feature_incompat_s))
        feature_ro_compat = self.lsb2int(f.read(4))
        feature_ro_compat_s = self.map_bitmap(
            feature_ro_compat,
            (
                (0b001, "sparse_super"),
                (0b010, "large_file"),
                (0b100, "btree_dir"),
            ),
        )
        record("Read-only features bitmap", "{0:03b} ({1})".format(feature_ro_compat, feature_ro_compat_s))

        # Bytes 104-119
        record("128-bit filesystem identifier", "{0}".format(self.uuid(hexlify(f.read(16)))))

        # Bytes 120-135
        record("Volume name", "{0}".format(lsb2ascii(f.read(16))))

        # Bytes 136-199
        record("Path of last mount point", "{0}".format(lsb2ascii(f.read(64))))

        # Bytes 200-205
        algo_bitmap = self.lsb2int(f.read(4))
        algo_bitmap_s = self.map_bitmap(
            algo_bitmap,
            (
                (0b00001, "lzv1"),
                (0b00010, "lzrw3a"),
                (0b00100, "gzip"),
                (0b01000, "bzip3"),
                (0b10000, "lzo"),
            ),
        )
        record("Compression Algorithm", "{0:05b} ({1})".format(algo_bitmap, algo_bitmap_s))
        record("Number of blocks to preallocate", "{0:d}".format(self.lsb2int(f.read(1))))
        record("Number of blocks to preallocate for dirs", "{0:d}".format(self.lsb2int(f.read(1))))

        # Bytes 208-235
        f.read(2)  # Padding
        record("Journal UUID", "{0}".format(self.uuid(hexlify(f.read(16)))))
        record("Journal inode number", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Journal device number", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Journal last orphan", "{0:d}".format(self.lsb2int(f.read(4))))

        # Bytes 236-255
        record(
            "Hash seed",
            "{0:d}".format(self.lsb2int(f.read(4))),
        )
        record("Hash seed", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Hash seed", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Hash seed", "{0:d}".format(self.lsb2int(f.read(4))))
        record("Hash version", "{0:d}".format(self.lsb2int(f.read(1))))
        f.read(3)  # Padding

        # Bytes 256-263
        defm_options = self.lsb2int(f.read(4))
        defm_options_s = self.map_bitmap(
            defm_options,
            (
                (0b00001, "debug"),
                (0b00010, "bsdgroups"),
                (0b00100, "xattr_user"),
                (0b01000, "acl"),
                (0b10000, "uid16"),
            ),
        )
        record("Default mount options", "{0:05b} ({1})".format(defm_options, defm_options_s))
        record("First meta block group ID", "{0:d}".format(self.lsb2int(f.read(4))))
        return report

    @classmethod
    def check_is_ext(cls, fp):
        fp.seek(0)
        fp.seek(2 * BLOCKSIZE + 48 + 4 + 2 + 2)
        data = fp.read(2)
        if not data:
            return False
        magic_signature = cls.lsb2int(data)
        return magic_signature == 0xEF53


def run():
    import argparse

    help_msg = (
        "This is a script to analyze the superblock of an ext2/ext3 formatted file.\n\n"
        "Such a file can be created as follows:\n"
        "    $ dd count=4096 if=/dev/zero of=filesystem.ext3\n"
        "    $ mkfs.ext3 filesystem.ext3\n\n"
        "It can be mounted with :\n"
        "    $ sudo mount -t ext3 -o loop filesystem.ext3 /mnt/mountpoint\n"
    )

    parser = argparse.ArgumentParser(description=help_msg, formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest="command")
    hexdump = subparsers.add_parser("hexdump", help="Print hexdump of EXT superblock")
    hexdump.add_argument("filename", help="Path to file with EXT filesystem")

    analyze = subparsers.add_parser("analyze", help="Read and parse EXT superblock")
    analyze.add_argument("-j", "--json", help="Output report as json", action="store_true")
    analyze.add_argument("filename", help="Path to file with EXT filesystem")

    args = parser.parse_args()

    if not os.path.exists(args.filename) or os.path.isdir(args.filename):
        print("Error, can't find file '{}'".format(args.filename))
        sys.exit(1)

    with open(args.filename, "rb") as fp:
        if not ExtSuperblock.check_is_ext(fp):
            print("Error, file '{}' does not contain EXT superblock".format(args.filename))
            sys.exit(1)

        ext_block = ExtSuperblock(fp)

        if args.command == "hexdump":
            print(ext_block.hexdump())
        elif args.command == "analyze":
            report = ext_block.analyze()
            if args.json:
                import json

                print(json.dumps(report.as_dict(), indent=2))
            else:
                print(report)


if __name__ == "__main__":
    run()
