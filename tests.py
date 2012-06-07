import re
from extract_information import extract_from_pdf

ELEMENTARY_SCHOOL_POINTS = {
    'xml/ES/201-Bass, John C ES.xml': {
        'School': 'Bass, John C ES',
        'Academic Growth': '31',
        'Academic Achievement': '12.9',
        'Academic Growth Gaps': '9',
        'Other Indicators': '10',
        'AYP': 'No',
        'Focus Goal': '5 Percent Bonus',
        'Total Score': '69.18',
     },
}

def check_elementary_school_values(fname):
    correct_values = ELEMENTARY_SCHOOL_POINTS.get(fname)
    info = extract_from_pdf(fname, 'ES')

    test_keys = ['School', 'Academic Growth', 'Academic Achievement', 'Academic Growth Gaps',
                 'Other Indicators', 'AYP', 'Focus Goal', 'Total Score']
    for key in test_keys:
        assert_string = "got: '%s', correct: '%s' for key '%s'" % (info[key], correct_values[key], key)
        assert info[key] == correct_values[key], assert_string

def test_elementary_school():
    for fname in ELEMENTARY_SCHOOL_POINTS.iterkeys():
        check_elementary_school_values.description = "Elementary school: '%s'" % re.search('\d{3}-([^.]+)\.xml$', fname).group(1)
        yield check_elementary_school_values, fname

def test_middle_school():
    pass

def test_high_scool():
    pass
