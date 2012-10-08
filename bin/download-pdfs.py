#!/usr/bin/env python

"""
Download the SPF reports for each school listed in the Excel
spreadsheet.
"""

import os
import re
import xlrd
import argparse

# Set up parser so we can run it like this:
# $ download-pdfs.py -o pdf/ schools.xls
parser = argparse.ArgumentParser()
parser.add_argument('input', help='name of the spreadsheet', metavar='xls')
parser.add_argument('-o', '--output-dir', help='where to place PDF files', default='.')
args = parser.parse_args()

# Open the Excel file and grab the first sheet
xls = xlrd.open_workbook(args.input, formatting_info=True)
sheet = xls.sheet_by_index(0)

# Create the output directory if it doesn't exist
if not os.path.isdir(args.output_dir):
    os.mkdir(args.output_dir)

# For each school
for row in range(sheet.nrows):
    values = sheet.row_values(row, 0, 2)

    school_name = values[0] # Column 1
    school_type = values[1] # Column 2

    # Skip empty lines
    if not school_name:
        continue

    # Grab the the link address in the first column. If there
    link = sheet.hyperlink_map.get((row, 0)).url_or_path

    # Given the link, extract out all of the digits between the last
    # '/' and the end of the string. This will be our school ID.
    school_id = int(re.search('/(\d+)$', link).group(1))

    # Create the URL
    url = "http://ccsd.net/district/growth-model/perfdata/{0}/SPF/{1}SPF.pdf"
    url = url.format(school_type, school_id)

    # Create the output filename
    output = "%d-%s.pdf" % (school_id, school_name)
    output = output.replace('/', '-')
    output = os.path.join(args.output_dir, output)

    if not os.path.exists(output):
        print (url, output)

    # Download the URL with wget, storing it under 'output'
    # os.system("wget {} -O '{}'".format(url, output))
