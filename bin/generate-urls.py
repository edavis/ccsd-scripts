#!/usr/bin/env python

"""
Given the CSV created by ccsd-school-ids.py (along with some
hand-editing), create a 'urls.txt' to feed into cURL to bulk-download
CCSD's SPF reports.
"""

import tablib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("-o", "--output", default="urls.txt")
args = parser.parse_args()

schools = tablib.Dataset(headers=("Type", "ID", "School Name"))
schools.csv = open(args.input).read()

# http://ccsd.net/district/growth-model/perfdata/ES/SPF/272SPF.pdf
url_template = "http://ccsd.net/district/growth-model/perfdata/%(school_type)s/SPF/%(school_id)sSPF.pdf"

output = open(args.output, 'w')

for school in schools:
    (school_type, school_id, school_name) = school
    url = url_template % {"school_type": school_type,
                          "school_id": school_id}

    output.write('url = "%s"\noutput = "%s-%s.pdf"\n\n' % (url, school_id, school_name))
