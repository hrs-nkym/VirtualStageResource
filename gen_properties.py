#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exports CSV file from google spreadsheet and
Generates Java Properties file.

Usage:

    $ export SHEET_ID=(Spreadsheet ID hash)
    $ export SHEET_GID=(Spreadsheet GID number)
    $ python gen_properties.py > Bundle_ja.properties

    or

    $ python prop.py --sheet-id=(Spreadsheet ID hash) \
                     --sheet-gid=(Spreadsheet GID number) \
                     > Bundle_ja.properties
"""


from __future__ import print_function, unicode_literals


# XXX: this should be removed from repository.
# use command line arguments or environment variables, instead.
SHEET_ID = "1rtIBZNy-An7dujla4_HmX6yEv6PxcBiJexA3Ex7ZGZo"
SHEET_GID = 1828300565

# constants
GDRIVE_HOME = "https://docs.google.com"
EXPORT_URL = "{0}/spreadsheets/d/{1}/export?format=csv&id={1}&gid={2}"


import csv
import io
import os
import logging


try:
    # Python 3.x
    from urllib.request import urlretrieve

except ImportError:
    # Python 2.x
    from urllib import urlretrieve


try:
    # Check Python version by naming "apply"
    # it was dropped in 3.x
    apply
except NameError:
    # Python 3.x: csv module supports unicode
    csv_reader = csv.reader
else:
    # Python 2.x: csv module requires bytes stream.
    @apply
    def csv_reader(_encoding="utf-8"):
        """
        build unicode csv reader

        snippets was copies from:
        https://docs.python.org/2/library/csv.html#examples
        """

        def encoder(unicode_csv_data):
            for line in unicode_csv_data:
                yield line.encode(_encoding)

        def reader(unicode_csv_data, dialect=csv.excel, **kwargs):
            # csv.py doesn't do Unicode; encode temporarily as UTF-8:
            csv_reader = csv.reader(encoder(unicode_csv_data),
                                    dialect=dialect, **kwargs)
            for row in csv_reader:
                # decode UTF-8 back to Unicode, cell by cell:
                yield [unicode(cell, _encoding) for cell in row]

        return reader


def unicode_csv_reader(path, encoding="utf-8"):
    """CSV reader wrapper
    """
    with io.open(path, encoding=encoding) as stream:
        next(stream)  # Skip header
        for row in csv_reader(stream):
            yield row


def export_spreadsheet(sheet_id, sheet_gid, dest_path):
    """Exports google spreadsheet data as CSV
    """
    url = EXPORT_URL.format(GDRIVE_HOME, sheet_id, sheet_gid)
    urlretrieve(url, dest_path)


def main(sheet_id, sheet_gid, tmp_file="_tmp.csv"):
    """
    """

    # Ensure delete temporary file
    try:
        import atexit
    except ImportError:
        pass
    else:
        @atexit.register
        def _cleanup():
            if os.path.isfile(tmp_file):
                os.unlink(tmp_file)

    # Exports csv
    export_spreadsheet(sheet_id, sheet_gid, tmp_file)
    assert os.path.isfile(tmp_file)

    # Convert to unicode-escape (Java properties file requires)
    conv = lambda x: x.encode("unicode-escape").decode("latin-1")

    for row in unicode_csv_reader(tmp_file):
        key = row[0]
        value = row[2]

        # Key must not contain "=" separator
        assert "=" not in key

        # Skip invalid blank key
        if not key:
            continue

        # Section marker
        if key.startswith("#"):
            print("\n{0}".format(key))
            continue

        # Output Key=Value pair
        print("{0}={1}".format(key, conv(value)))


if __name__ == "__main__":
    from argparse import ArgumentParser

    # initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    # parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-id", "--sheet-id",
                        default=os.environ.get('SHEET_ID', SHEET_ID))
    parser.add_argument("-gid", "--sheet-gid",
                        default=os.environ.get('SHEET_GID', SHEET_GID))

    options = parser.parse_args()
    if options.sheet_id and options.sheet_gid:
        main(options.sheet_id, options.sheet_gid)
    else:
        logging.error("Missing sheet id/gid")
