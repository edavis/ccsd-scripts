#!/usr/bin/env python

"""
Now we're cooking.

This script parses out the important bits from the XML representations
of the SPF PDFs generated by pdf2txt.py (via pdfminer).

We have create separate elementary and middle school maps because --
of course -- the PDFs are slightly different.

Unfortunately we can't use any sort of "clean" XPath that relies on ID
numbers as they change from PDF to PDF. Therefore, we look in the
@bbox attribute for a given set of coordinates.

It ain't pretty, but it works.
"""

import re
import tablib
from lxml import etree
from ConfigParser import SafeConfigParser

DIGITS_ONLY = {'Academic Achievement', 'Other Indicators'}

# Cache the compiled regexes under the `coord` key
COMMON_BOUNDS = {}

def create_boundaries(coord, default_size=10):
    """
    Generate a coordinate matching regexp that can do "fuzzy matching."

    The PDFs provided by CCSD are programatically generated, but the
    point locations for certain elements are not identical between
    each PDF.  This means we can't do a simple search for identical
    @bbox attribute values and expect it to work.

    The differences between point locations are usually not large, but
    they sometimes can be.  Here's what we do:

    Given the location point '663.000,313.440,699.454,323.989' we will
    take each whole number (e.g., 663, 313, 699, 323) and (by default)
    create a range from [n-default_size, n+default_size] (inclusive).

    We then '|'-join each number in the range so it becomes
    essentially an OR statement.  So with a default_size=5, the above
    coordinate point becomes:

    r'(658\.\d{3}|659\.\d{3}|...|667\.\d{3}|668\.\d{3}),(308\.\d{3}...),...

    EXCEPT, sometimes a particular digit (e.g., 313) will need to be
    (way) larger than default_size but you don't want each digit
    getting that treatment.

    In this case, after each digit's fractional part an optional ':N'
    can be supplied which will set that digit's "range."  For example:
    '663.000:10' will range between 653 and 673. When ':N' is omitted,
    the digit uses the default_size.
    """
    if coord in COMMON_BOUNDS:
        result = COMMON_BOUNDS[coord]
    else:
        s = []
        args = re.findall('(\d+)[.]\d{3}:?(\d*)', coord)
        for arg, size in args:
            size = int(size) if size else default_size
            arg = int(arg)
            result = '(' + '|'.join("%d\.\d{3}" % elem for elem in xrange(arg - size, arg + size + 1)) + ')'
            s.append(result)
        result = re.compile(','.join(s))
        COMMON_BOUNDS[coord] = result
    return result

def extract_text(textbox, category):
    """
    Given a textbox, return its concat'd text elements.
    """
    text = textbox.xpath("./textline/text[@bbox]/text()")
    s = ''.join(text).strip()
    return re.sub('[^\d.]+', '', s) if category in DIGITS_ONLY else s

def process_page(page):
    ret = {}
    keys_seen = set()
    for textbox in page['page']:
        for category, location in page['config']:
            keys_seen.add(category)
            match = create_boundaries(location).search(textbox.attrib['bbox'])
            if match and category not in ret:
                ret[category] = extract_text(textbox, category)

    missing_keys = keys_seen - set(ret.keys())
    for missing_key in missing_keys:
        ret[missing_key] = '*** Missing value ***'

    return ret

def extract_from_pdf(fname, config):
    """
    Return a dictionary of {category: value} for a given school XML file.
    """
    doc = etree.parse(fname)
    ret = {'School': re.search('\d\d\d-(.+)\.xml$', fname).group(1)}

    pages = [
        dict(config=config.items('p1'), page=doc.xpath("//page[@id='1']//textbox")),
        dict(config=config.items('p2'), page=doc.xpath("//page[@id='2']//textbox")),
        dict(config=config.items('p3'), page=doc.xpath("//page[@id='3']//textbox")),
    ]

    for page in pages:
        ret.update(process_page(page))

    return ret

def main():
    import argparse
    from operator import itemgetter
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs='+', metavar="XML")
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()

    output = tablib.Dataset()
    config = SafeConfigParser()
    config.optionxform = lambda value: value
    config.read([args.config])

    for fname in args.input:
        print "Parsing '%s'..." % fname
        info = extract_from_pdf(fname, config)
        values = []

        if not output.headers:
            output.headers = sorted(info.keys())

        for k, v in sorted(info.iteritems(), key=itemgetter(0)):
            values.append(v)

        output.append(values)

    print "Writing to '%s'..." % args.output
    with open(args.output, 'wb') as fp:
        fp.write(output.csv)

if __name__ == "__main__":
    main()
