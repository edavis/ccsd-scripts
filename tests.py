import re
from extract_information import extract_from_pdf

ELEMENTARY_SCHOOL_POINTS = {
    'xml/ES/201-Bass, John C ES.xml': {
        'School'               : 'Bass, John C ES',

        # p1
        'Academic Growth'      : '31',
        'Academic Achievement' : '12.9',
        'Academic Growth Gaps' : '9',
        'Other Indicators'     : '10',
        'AYP'                  : 'No',
        'Focus Goal'           : '5 Percent Bonus',
        'Total Score'          : '69.18',

        # p2
        'Academic Growth/Math'                            : '17',
        'Academic Growth/Math/Count'                      : '258',
        'Academic Growth/Math/MGP'                        : '56',
        'Academic Growth/Reading'                         : '14',
        'Academic Growth/Reading/Count'                   : '259',
        'Academic Growth/Reading/MGP'                     : '48',

        'Academic Achievement/Math'                       : '5',
        'Academic Achievement/Math/Count'                 : '401',
        'Academic Achievement/Math/Pct. Proficient'       : '71.82%',

        'Academic Achievement/Math/Catch Up'              : '3',
        'Academic Achievement/Math/Catch Up/Count'        : '84',
        'Academic Achievement/Math/Catch Up/Percent'      : '41.67%',
        'Academic Achievement/Math/Catch Up/Reduction'    : '17.17%',

        'Academic Achievement/Math/Keep Up'               : '2',
        'Academic Achievement/Math/Keep Up/Count'         : '174',
        'Academic Achievement/Math/Keep Up/Percent'       : '67.24%',
        'Academic Achievement/Math/Keep Up/Reduction'     : '44.81%',

        'Academic Achievement/Reading'                    : '2.5',
        'Academic Achievement/Reading/Count'              : '402',
        'Academic Achievement/Reading/Pct. Proficient'    : '63.68%',

        'Academic Achievement/Reading/Catch Up'           : '0',
        'Academic Achievement/Reading/Catch Up/Count'     : '83',
        'Academic Achievement/Reading/Catch Up/Percent'   : '24.10%',
        'Academic Achievement/Reading/Catch Up/Reduction' : '0',

        'Academic Achievement/Reading/Keep Up'            : '0.4',
        'Academic Achievement/Reading/Keep Up/Count'      : '176',
        'Academic Achievement/Reading/Keep Up/Percent'    : '61.36%',
        'Academic Achievement/Reading/Keep Up/Reduction'  : '0',

        # p3
        # ===========================================================================
        # Growth Gaps/Reading
        # ===========================================================================
        'Growth Gaps/Math/FRLE'               : '3',
          'Growth Gaps/Math/FRLE/Count'       : '126',
          'Growth Gaps/Math/FRLE/MGP'         : '52',
          'Growth Gaps/Math/FRLE/MAGP'        : '51',
          'Growth Gaps/Math/FRLE/MAG'         : 'Yes',

        'Growth Gaps/Math/Minority'           : '3',
          'Growth Gaps/Math/Minority/Count'   : '162',
          'Growth Gaps/Math/Minority/MGP'     : '56',
          'Growth Gaps/Math/Minority/MAGP'    : '48',
          'Growth Gaps/Math/Minority/MAG'     : 'Yes',

        'Growth Gaps/Math/Disability'         : '0',
          'Growth Gaps/Math/Disability/Count' : '27',
          'Growth Gaps/Math/Disability/MGP'   : '33',
          'Growth Gaps/Math/Disability/MAGP'  : '55',
          'Growth Gaps/Math/Disability/MAG'   : 'No',

        'Growth Gaps/Math/LEP'                : '3',
          'Growth Gaps/Math/LEP/Count'        : '39',
          'Growth Gaps/Math/LEP/MGP'          : '61',
          'Growth Gaps/Math/LEP/MAGP'         : '52',
          'Growth Gaps/Math/LEP/MAG'          : 'Yes',

        # ===========================================================================
        # Growth Gaps/Reading
        # ===========================================================================
        'Growth Gaps/Reading/FRLE': '0',
          'Growth Gaps/Reading/FRLE/Count': '126',
          'Growth Gaps/Reading/FRLE/MGP': '41',
          'Growth Gaps/Reading/FRLE/MAGP': '53',
          'Growth Gaps/Reading/FRLE/MAG': 'No',

        'Growth Gaps/Reading/Minority': '0',
          'Growth Gaps/Reading/Minority/Count': '162',
          'Growth Gaps/Reading/Minority/MGP': '45',
          'Growth Gaps/Reading/Minority/MAGP': '50',
          'Growth Gaps/Reading/Minority/MAG': 'No',

        'Growth Gaps/Reading/Disability': '0',
          'Growth Gaps/Reading/Disability/Count': '27',
          'Growth Gaps/Reading/Disability/MGP': '38',
          'Growth Gaps/Reading/Disability/MAGP': '80',
          'Growth Gaps/Reading/Disability/MAG': 'No',

        'Growth Gaps/Reading/LEP': '0',
          'Growth Gaps/Reading/LEP/Count': '40',
          'Growth Gaps/Reading/LEP/MGP': '44',
          'Growth Gaps/Reading/LEP/MAGP': '59',
          'Growth Gaps/Reading/LEP/MAG': 'No',

        'Other Factors/Avg. Daily Attendance'   : '2',
        'Other Factors/LEP (>24pt gain)'        : '1',
        'Other Factors/LEP (Attain lvl 5)'      : '1',
        'Other Factors/IEP'                     : '2',
        'Other Factors/6th Grade'               : '0',
        'Other Factors/Student Survey Positive' : '1',
        'Other Factors/Parent Engagement Plan'  : '3',
    },

    'xml/ES/202-Wolff, Elise L ES.xml': {
        'Total Score'          : '70.7',
        'AYP'                  : 'AYP',
        'Academic Growth/Math' : '10',
    },

    'xml/ES/203-Tarr, Sheila R ES.xml': {
        'Academic Achievement' : '20',
        'Other Indicators'     : '9',
        'Academic Growth Gaps' : '12',
    },

    'xml/ES/204-Staton, Ethel W ES.xml': {
        'Academic Achievement/Math/Catch Up/Reduction': '0',
    },

    'xml/ES/205-Snyder, William E ES.xml': {
        'Other Indicators'     : '10.5',
        'Total Score'          : '88.51',
    },

    'xml/ES/209-Bonner, John W ES.xml': {
        'Academic Achievement/Reading/Catch Up/Reduction' : '22.65%',
        'Academic Achievement/Reading/Keep Up/Reduction'  : '45.45%',

        'Growth Gaps/Math/FRLE'          : '3',
        'Growth Gaps/Math/Minority'      : '3',
        'Growth Gaps/Math/Disability'    : 'NA',
        'Growth Gaps/Math/LEP'           : 'NA',

        'Growth Gaps/Reading/FRLE'       : '3',
        'Growth Gaps/Reading/Minority'   : '3',
        'Growth Gaps/Reading/Disability' : 'NA',
        'Growth Gaps/Reading/LEP'        : 'NA',

        'Other Factors/Avg. Daily Attendance'   : '2',
        'Other Factors/LEP (>24pt gain)'        : 'NA',
        'Other Factors/LEP (Attain lvl 5)'      : 'NA',
        'Other Factors/IEP'                     : '2',
        'Other Factors/6th Grade'               : '2',
        'Other Factors/Student Survey Positive' : '1',
        'Other Factors/Parent Engagement Plan'  : '3',
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
