#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


"""Generate markdown for preview

Output encoding is upto the runtime environment.
Set `PYTHONIOENCODING` environment variable,
Python interpreter will encode the standard output.


Usage:

    $ PYTHONIOENCODING=utf-8 python gen_properties_md.py \
         < Bundle_ja.properties > Bundle_ja.md


"""


import sys
import fileinput


def main():
    """Convert java properties (UTF-16) file to markdown
    """

    decode = lambda x: x.encode("latin-1").decode("unicode-escape")

    for line in fileinput.input():
        line = line.strip()
        if not line:  # Skip empty line
            continue
        elif line.startswith("#"):  # Section marker
            print()
            print()
            print("## {}".format(line.lstrip("#").title()))
            print()
        elif "=" in line:
            # NOTE: value may contains Markdown notation.
            # This code doesn't check it now.
            key, value = line.split("=", 1)
            print("| {:20} | {:40} |".format(key, decode(value)))
        else:
            # Program should not arrive here, except coverage test.
            raise RuntimeError("Invalid file input")


if __name__ == "__main__":
    sys.exit(main())

