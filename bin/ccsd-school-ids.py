#!/usr/bin/env python

"""
Given an HTML snippet of school contact information from ccsd.net,
generate a CSV of school ID numbers and names.
"""

import tablib
import argparse
from lxml.html import parse

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("-o", "--output", default="output.csv")
args = parser.parse_args()

doc = parse(args.input)

school_ids = tablib.Dataset(headers=("ID", "School Name"))

for a in doc.xpath("//td[position()=1]/a"):
    school_id = dict(a.items()).get('href')
    school_name = a.text
    school_ids.append([int(school_id), school_name])

with open(args.output, 'wb') as fp:
    fp.write(school_ids.csv)
