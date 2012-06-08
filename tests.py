import re
from extract_information import extract_from_pdf

ELEMENTARY_SCHOOL_POINTS = {
    'xml/ES/201-Bass, John C ES.xml': {
        'School'               : 'Bass, John C ES',

        # p1
        'Academic Growth'         : '31',
        'Academic Achievement'    : '12.9',
        'Academic Growth Gaps'    : '9',
        'Other Indicators'        : '10',
        'AYP'                     : 'No',
        'Focus Goal'              : '5 Percent Bonus',
        'Total Score'             : '69.18',

        # p2
        'Academic Growth/Math'    : '17',
        'Academic Growth/Reading' : '14',
    },

    'xml/ES/202-Wolff, Elise L ES.xml': {
        'Total Score'          : '70.7',
        'AYP'                  : 'AYP',
    },

    'xml/ES/203-Tarr, Sheila R ES.xml': {
        'Academic Achievement' : '20',
        'Other Indicators'     : '9',
        'Academic Growth Gaps' : '12',
    },

    'xml/ES/205-Snyder, William E ES.xml': {
        'Other Indicators'     : '10.5',
        'Total Score'          : '88.51',
    },

    'xml/ES/212-King, Jr, Martin Luther ES.xml': {
        'AYP': 'Watch',
    },

    'xml/ES/214-Park, John S ES.xml': {
        'Academic Growth Gaps': '10.5',
    },

    'xml/ES/305-Cozine, Steve ES.xml': {
        'Total Score': '80',
    },
}

def check_elementary_school_values(fname):
    correct_values = ELEMENTARY_SCHOOL_POINTS.get(fname)
    info = extract_from_pdf(fname, 'ES')

    for key in correct_values.iterkeys():
        assert_string = "got: %r, correct: %r for key: %r" % (info[key], correct_values[key], key)
        assert info[key] == correct_values[key], assert_string

def test_elementary_school():
    for fname in ELEMENTARY_SCHOOL_POINTS.iterkeys():
        yield check_elementary_school_values, fname

def test_middle_school():
    pass

def test_high_scool():
    pass
