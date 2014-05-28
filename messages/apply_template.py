#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

"""
Generate HTML Pre-View

Usage:

    $ python ../gen_properties.py \
        --sheet-id=1rtIBZNy-An7dujla4_HmX6yEv6PxcBiJexA3Ex7ZGZo \
        --sheet-gid=1078035474 > messages_ja.properties
    $ python ./apply_template.py > vs-site-ja-preview.html

For windows:

    set "PYTHONIOENCODING" environment variable "utf-8"  for
    standard output encoding.

"""

import io
import re
import sys


def read_properties(filepath, _encoding="latin-1"):
    # NOTE: the open encoding option can't be unicode-escape
    # value may contained escaped line-break character.

    decode = lambda value: value.encode(_encoding).decode("unicode-escape")
    parse = lambda line: line.rstrip().split("=", 1)

    with io.open(filepath, encoding=_encoding) as stream:
        for line in stream:
            if "=" in line:
                key, value = parse(line)
                yield key, decode(value)


def replace_template_vars(template, properties):
    """
    >>> replace_template_vars("Hello {{ name }} !", {'name': 'test'})
    'Hello test !'
    """
    return re.sub(r"\{\{ ([\w\.]+?) \}\}",
                  lambda m: properties.get(m.group(1), ""),
                  template)


if __name__ == "__main__":
    # NOTE: template.html was copied from official site.
    # This file will not be updated automatically, I had to modify by hands.
    # 1) add base tag
    # 2) replace property variables

    with io.open("template.html", encoding="utf-8") as stream:
        template = stream.read()
        properties = dict(read_properties("messages_ja.properties"))
        content = replace_template_vars(template, properties)
        print(content)
