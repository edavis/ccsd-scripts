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

DIGITS_ONLY = {'Academic Achievement', 'Other Indicators'}

# Cache lookup so the '|' joined fuzzy ranges don't have to be
# completely regenerated each time.
#
# Without this, takes 2 and a half minutes to parse all elementary
# school XML files. With this, down to 30 seconds.
COMMON_RANGES = {}

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
    s = []
    args = re.findall('(\d+)[.]\d{3}:?(\d*)', coord)
    for arg, size in args:
        size = int(size) if size else default_size
        arg = int(arg)
        if (arg, size) in COMMON_RANGES:
            result = COMMON_RANGES[(arg, size)]
        else:
            result = '(' + '|'.join("%d\.\d{3}" % elem for elem in xrange(arg - size, arg + size + 1)) + ')'
            COMMON_RANGES[(arg, size)] = result
        s.append(result)
    return re.compile(','.join(s))

def extract_text(textbox, category):
    """
    Given a textbox, return its concat'd text elements.
    """
    text = textbox.xpath("./textline/text[@bbox]/text()")
    s = ''.join(text).strip()
    return re.sub('[^\d.]+', '', s) if category in DIGITS_ONLY else s

def extract_from_pdf(fname, school_type):
    """
    Return a dictionary of {category: value} for a given school XML file.
    """
    doc = etree.parse(fname)
    ret = {'School': re.search('\d\d\d-([^.]+)\.xml$', fname).group(1)}

    if school_type == 'ES':
        p1_categories = {
            "Academic Growth"      : "476.280,    510.359, 488.405,    520.672",
            "Academic Achievement" : "476.040,    480.359, 488.285:50, 490.672",
            "Academic Growth Gaps" : "479.280,    450.359, 485.402,    460.672",
            "Other Indicators"     : "476.280,    420.359, 488.405:50, 430.672",
            "AYP"                  : "669.000,    388.565, 682.196,    398.150",
            "Focus Goal"           : "639.960,    355.565, 714.096,    365.150",
            "Total Score"          : "663.000:20, 313.440, 699.454,    323.989",
        }

        textboxes = doc.xpath("//page[@id='1']//textbox")
        for textbox in textboxes:
            for category, location in p1_categories.iteritems():
                match = create_boundaries(location).search(textbox.attrib['bbox'])
                if match and category not in ret:
                    ret[category] = extract_text(textbox, category)

        # Fill in any missing values
        missing_keys = set(p1_categories.keys()) - set(ret.keys())
        for missing_key in missing_keys:
            ret[missing_key] = '*** Missing value ***'

        ###########################################################################
        p2_categories = {
            # ===========================================================================
            # Academic Growth/Math
            # ===========================================================================
            "Academic Growth/Math"       : "221.640,495.359,233.885,505.672",
            "Academic Growth/Math/Count" : "419.280,495.359,437.648,506.152",
            "Academic Growth/Math/MGP"   : "518.880,495.359,531.125,506.152",

            # ===========================================================================
            # Academic Growth/Reading
            # ===========================================================================
            "Academic Growth/Reading"       : "221.640,465.359,233.885,475.672",
            "Academic Growth/Reading/Count" : "419.880,465.359,438.248,476.152",
            "Academic Growth/Reading/MGP"   : "518.160,465.359,530.405,476.152",

            # ===========================================================================
            # Academic Achievement/Math
            # ===========================================================================
            "Academic Achievement/Math"                    : "224.640,375.359,230.763,385.672",
            "Academic Achievement/Math/Count"              : "419.880,375.359,438.248,386.152",
            "Academic Achievement/Math/Pct. Proficient"    : "513.840,375.359,549.842,386.152",

            "Academic Achievement/Math/Catch Up"           : "224.640,345.359,230.763,355.672",
            "Academic Achievement/Math/Catch Up/Count"     : "422.880,345.359,435.125,356.152",
            "Academic Achievement/Math/Catch Up/Percent"   : "605.160,345.359,641.162,356.152",
            "Academic Achievement/Math/Catch Up/Reduction" : "698.040:15,345.359,734.042:15,356.152",

            "Academic Achievement/Math/Keep Up"            : "224.640,315.359,230.763,325.672",
            "Academic Achievement/Math/Keep Up/Count"      : "419.880,315.359,438.248,326.152",
            "Academic Achievement/Math/Keep Up/Percent"    : "605.160,315.359,641.162,326.152",
            "Academic Achievement/Math/Keep Up/Reduction"  : "698.040:15,315.359,734.042:15,326.152",

            # ===========================================================================
            # Academic Achievement/Reading
            # ===========================================================================
            "Academic Achievement/Reading"                : "219.960,255.239,235.445,265.552",
            "Academic Achievement/Reading/Count"          : "419.280,255.239,437.648,266.032",
            "Academic Achievement/Reading/Catch Up"       : "224.640,225.239,230.763,235.552",
            "Academic Achievement/Reading/Catch Up/Count" : "422.880,225.239,435.125,236.032",
            "Academic Achievement/Reading/Keep Up"        : "219.960,195.239,235.445,205.552",
            "Academic Achievement/Reading/Keep Up/Count"  : "419.880,195.239,438.248,206.032",
        }

        textboxes = doc.xpath("//page[@id='2']//textbox")
        for textbox in textboxes:
            for category, location in p2_categories.iteritems():
                match = create_boundaries(location).search(textbox.attrib['bbox'])
                if match and category not in ret:
                    ret[category] = extract_text(textbox, category)

        # Fill in any missing values
        missing_keys = set(p2_categories.keys()) - set(ret.keys())
        for missing_key in missing_keys:
            ret[missing_key] = '*** Missing value ***'

        ###########################################################################
        p3_categories = {
            "Growth Gaps/Math/FRLE"               : "234.360,519.725,238.916,527.874",
              "Growth Gaps/Math/FRLE/Count"       : "421.560,519.725,435.229,527.874",
              "Growth Gaps/Math/FRLE/MGP"         : "513.720,519.725,522.833,527.874",
              "Growth Gaps/Math/FRLE/MAGP"        : "618.600,519.725,627.713,527.874",
              "Growth Gaps/Math/FRLE/MAG"         : "712.560,519.725,725.402,527.874",

            "Growth Gaps/Math/Minority"           : "234.360,498.725,238.916,506.874",
              "Growth Gaps/Math/Minority/Count"   : "421.560,498.725,435.229,506.874",
              "Growth Gaps/Math/Minority/MGP"     : "513.720,498.725,522.833,506.874",
              "Growth Gaps/Math/Minority/MAGP"    : "618.600,498.725,627.713,506.874",
              "Growth Gaps/Math/Minority/MAG"     : "712.560,498.725,725.402,506.874",

            "Growth Gaps/Math/Disability"         : "234.360,477.725,238.916,485.874",
              "Growth Gaps/Math/Disability/Count" : "423.840,477.725,432.953,485.874",
              "Growth Gaps/Math/Disability/MGP"   : "513.720,477.725,522.833,485.874",
              "Growth Gaps/Math/Disability/MAGP"  : "618.600,477.725,627.713,485.874",
              "Growth Gaps/Math/Disability/MAG"   : "713.640,477.725,724.320,485.874",

            "Growth Gaps/Math/LEP"                : "234.360,456.485,238.916,464.634",
              "Growth Gaps/Math/LEP/Count"        : "423.840,456.485,432.953,464.634",
              "Growth Gaps/Math/LEP/MGP"          : "513.720,456.485,522.833,464.634",
              "Growth Gaps/Math/LEP/MAGP"         : "618.600,456.485,627.713,464.634",
              "Growth Gaps/Math/LEP/MAG"          : "712.560,456.485,725.402,464.634",

            "Growth Gaps/Reading/FRLE"              : "234.360,399.725,238.916,407.874",
            "Growth Gaps/Reading/Minority"          : "234.360,399.725,238.916,407.874",
            "Growth Gaps/Reading/Disability"        : "231.240,378.725,242.162,386.874",
            "Growth Gaps/Reading/LEP"               : "231.240,357.365,242.162,365.514",

            "Other Factors/Avg. Daily Attendance"   : "234.360,285.605,238.916,293.754",
            "Other Factors/LEP (>24pt gain)"        : "231.240,267.605,242.162,275.754",
            "Other Factors/LEP (Attain lvl 5)"      : "231.240,249.485,242.162,257.634",
            "Other Factors/IEP"                     : "234.360,219.605,238.916,227.754",
            "Other Factors/6th Grade"               : "234.360,189.605,238.916,197.754",
            "Other Factors/Student Survey Positive" : "234.360,171.605,238.916,179.754",
            "Other Factors/Parent Engagement Plan"  : "234.360,153.605,238.916,161.754",
        }

        textboxes = doc.xpath("//page[@id='3']//textbox")
        for textbox in textboxes:
            for category, location in p3_categories.iteritems():
                match = create_boundaries(location).search(textbox.attrib['bbox'])
                if match and category not in ret:
                    ret[category] = extract_text(textbox, category)

        # Fill in any missing values
        missing_keys = set(p3_categories.keys()) - set(ret.keys())
        for missing_key in missing_keys:
            ret[missing_key] = '*** Missing value ***'

    return ret

def main():
    import argparse
    from operator import itemgetter
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs='+', metavar="XML")
    parser.add_argument("-t", "--school-type")
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()

    output = tablib.Dataset()

    for fname in args.input:
        print "Parsing '%s'..." % fname
        info = extract_from_pdf(fname, args.school_type)
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
