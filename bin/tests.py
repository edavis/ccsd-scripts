import re
from ConfigParser import SafeConfigParser
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
        'Growth Gaps/Eligible': '22',

        # ===========================================================================
        # Growth Gaps/Reading
        # ===========================================================================
        'Growth Gaps/Math/FRLE'               : '3',
          'Growth Gaps/Math/FRLE/Eligible'    : '3',
          'Growth Gaps/Math/FRLE/Count'       : '126',
          'Growth Gaps/Math/FRLE/MGP'         : '52',
          'Growth Gaps/Math/FRLE/MAGP'        : '51',
          'Growth Gaps/Math/FRLE/MAG'         : 'Yes',

        'Growth Gaps/Math/Minority'           : '3',
          'Growth Gaps/Math/Minority/Eligible': '3',
          'Growth Gaps/Math/Minority/Count'   : '162',
          'Growth Gaps/Math/Minority/MGP'     : '56',
          'Growth Gaps/Math/Minority/MAGP'    : '48',
          'Growth Gaps/Math/Minority/MAG'     : 'Yes',

        'Growth Gaps/Math/Disability'         : '0',
          'Growth Gaps/Math/Disability/Eligible': '2',
          'Growth Gaps/Math/Disability/Count' : '27',
          'Growth Gaps/Math/Disability/MGP'   : '33',
          'Growth Gaps/Math/Disability/MAGP'  : '55',
          'Growth Gaps/Math/Disability/MAG'   : 'No',

        'Growth Gaps/Math/LEP'                : '3',
          'Growth Gaps/Math/LEP/Eligible'     : '3',
          'Growth Gaps/Math/LEP/Count'        : '39',
          'Growth Gaps/Math/LEP/MGP'          : '61',
          'Growth Gaps/Math/LEP/MAGP'         : '52',
          'Growth Gaps/Math/LEP/MAG'          : 'Yes',

        # ===========================================================================
        # Growth Gaps/Reading
        # ===========================================================================
        'Growth Gaps/Reading/FRLE': '0',
          'Growth Gaps/Reading/FRLE/Eligible': '3',
          'Growth Gaps/Reading/FRLE/Count': '126',
          'Growth Gaps/Reading/FRLE/MGP': '41',
          'Growth Gaps/Reading/FRLE/MAGP': '53',
          'Growth Gaps/Reading/FRLE/MAG': 'No',

        'Growth Gaps/Reading/Minority': '0',
          'Growth Gaps/Reading/Minority/Eligible': '3',
          'Growth Gaps/Reading/Minority/Count': '162',
          'Growth Gaps/Reading/Minority/MGP': '45',
          'Growth Gaps/Reading/Minority/MAGP': '50',
          'Growth Gaps/Reading/Minority/MAG': 'No',

        'Growth Gaps/Reading/Disability': '0',
          'Growth Gaps/Reading/Disability/Eligible': '2',
          'Growth Gaps/Reading/Disability/Count': '27',
          'Growth Gaps/Reading/Disability/MGP': '38',
          'Growth Gaps/Reading/Disability/MAGP': '80',
          'Growth Gaps/Reading/Disability/MAG': 'No',

        'Growth Gaps/Reading/LEP': '0',
          'Growth Gaps/Reading/LEP/Eligible': '3',
          'Growth Gaps/Reading/LEP/Count': '40',
          'Growth Gaps/Reading/LEP/MGP': '44',
          'Growth Gaps/Reading/LEP/MAGP': '59',
          'Growth Gaps/Reading/LEP/MAG': 'No',

        # ===========================================================================
        # Other Factors
        # ===========================================================================
        'Other Factors/Avg. Daily Attendance': '2',
          'Other Factors/Avg. Daily Attendance/Eligible': '2',
          'Other Factors/Avg. Daily Attendance/Rate 2010-2011': '95.90%',

        'Other Factors/LEP/Count': '52',

        'Other Factors/LEP (>24pt gain)': '1',
          'Other Factors/LEP (>24pt gain)/Eligible': '1',
          "Other Factors/LEP (>24pt gain)/Rate 2010-2011": "71.15%",
          "Other Factors/LEP (>24pt gain)/Rate 2009-2010": "81.16%",

        'Other Factors/LEP (Attain lvl 5)': '1',
          'Other Factors/LEP (Attain lvl 5)/Eligible': '1',
          "Other Factors/LEP (Attain lvl 5)/Rate 2010-2011": "25.00%",
          "Other Factors/LEP (Attain lvl 5)/Rate 2009-2010": "23.19%",

        'Other Factors/IEP': '2',
          'Other Factors/IEP/Eligible': '2',
          'Other Factors/IEP/Count': '87',

          "Other Factors/IEP (gte 80 pct)/Rate 2010-2011": "52.87%",
          "Other Factors/IEP (gte 80 pct)/Rate 2009-2010": "62.03%",

          "Other Factors/IEP (Gen Ed)/Rate 2010-2011": "67.86%",
          "Other Factors/IEP (Gen Ed)/Rate 2009-2010": "66.72%",

        'Other Factors/6th Grade': '0',
          'Other Factors/6th Grade/Eligible': '2',
          'Other Factors/6th Grade/Count': '145',
          'Other Factors/6th Grade/Rate 2010-2011': '33.10%',
          'Other Factors/6th Grade/Rate 2009-2010': '35.33%',

        'Other Factors/Student Survey Positive': '1',
          'Other Factors/Student Survey Positive/Eligible': '1',
          'Other Factors/Student Survey Positive/Count': '36',
          'Other Factors/Student Survey Positive/Rate 2010-2011': '96.03%',

        'Other Factors/Parent Engagement Plan': '3',
          'Other Factors/Parent Engagement Plan/Eligible': '3',
    },

    'xml/ES/202-Wolff, Elise L ES.xml': {
        'Total Score'          : '70.7',
        'AYP'                  : 'AYP',
        'Academic Growth/Math' : '10',

        'Growth Gaps/Math/Disability/Eligible': '0',
        'Growth Gaps/Math/LEP/Eligible': '0',
        'Growth Gaps/Reading/Disability/Eligible': '0',
        'Growth Gaps/Reading/LEP/Eligible': '0',

        'Growth Gaps/Eligible': '12',
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

MIDDLE_SCHOOL_POINTS = {
    'xml/MS/231-Fremont, John C Professional Development MS.xml': {
        'School'               : 'Fremont, John C Professional Development MS',
        'Academic Growth'      : '11',
        'Academic Achievement' : '0',
        'Academic Growth Gaps' : '0',
        'Other Indicators'     : '7.25',
        'AYP'                  : 'No',
        'Focus Goal'           : '5 Percent Bonus',
        'Total Score'          : '23.62',
    },

    'xml/MS/273-Rogich, Sig MS.xml': {
        # p1
        'Academic Growth'      : '31',
        'Academic Achievement' : '16.5',
        'Academic Growth Gaps' : '10.5',
        'Other Indicators'     : '9.5',
        'AYP'                  : 'AYP',
        'Focus Goal'           : '5 Percent Bonus',
        'Total Score'          : '73.88',

        # p2
        'Academic Growth/Math'                            : '17',
        'Academic Growth/Math/Count'                      : '1557',
        'Academic Growth/Math/MGP'                        : '54',
        'Academic Growth/Reading'                         : '14',
        'Academic Growth/Reading/Count'                   : '1556',
        'Academic Growth/Reading/MGP'                     : '52',

        'Academic Achievement/Math'                       : '5',
        'Academic Achievement/Math/Count'                 : '1667',
        'Academic Achievement/Math/Pct. Proficient'       : '84.22%',

        'Academic Achievement/Math/Catch Up'              : '3',
        'Academic Achievement/Math/Catch Up/Count'        : '263',
        'Academic Achievement/Math/Catch Up/Percent'      : '35.36%',
        'Academic Achievement/Math/Catch Up/Reduction'    : '19.02%',

        'Academic Achievement/Math/Keep Up'               : '2',
        'Academic Achievement/Math/Keep Up/Count'         : '1294',
        'Academic Achievement/Math/Keep Up/Percent'       : '82.38%',
        'Academic Achievement/Math/Keep Up/Reduction'     : '15.35%',

        'Academic Achievement/Reading'                    : '5',
        'Academic Achievement/Reading/Count'              : '1666',
        'Academic Achievement/Reading/Pct. Proficient'    : '71.01%',

        'Academic Achievement/Reading/Catch Up'           : '0',
        'Academic Achievement/Reading/Catch Up/Count'     : '278',
        'Academic Achievement/Reading/Catch Up/Percent'   : '18.71%',
        'Academic Achievement/Reading/Catch Up/Reduction' : '0',

        'Academic Achievement/Reading/Keep Up'            : '1.5',
        'Academic Achievement/Reading/Keep Up/Count'      : '1278',
        'Academic Achievement/Reading/Keep Up/Percent'    : '68.62%',
        'Academic Achievement/Reading/Keep Up/Reduction'  : '0',

        # p3
        'Growth Gaps/Eligible': '22',

        'Growth Gaps/Math/FRLE'               : '3',
          'Growth Gaps/Math/FRLE/Eligible'    : '3',
          'Growth Gaps/Math/FRLE/Count'       : '280',
          'Growth Gaps/Math/FRLE/MGP'         : '52',
          'Growth Gaps/Math/FRLE/MAGP'        : '38',
          'Growth Gaps/Math/FRLE/MAG'         : 'Yes',

        'Growth Gaps/Math/Minority'           : '3',
          'Growth Gaps/Math/Minority/Eligible': '3',
          'Growth Gaps/Math/Minority/Count'   : '628',
          'Growth Gaps/Math/Minority/MGP'     : '53',
          'Growth Gaps/Math/Minority/MAGP'    : '28',
          'Growth Gaps/Math/Minority/MAG'     : 'Yes',

        'Growth Gaps/Math/Disability'         : '0',
          'Growth Gaps/Math/Disability/Eligible': '2',
          'Growth Gaps/Math/Disability/Count' : '95',
          'Growth Gaps/Math/Disability/MGP'   : '35',
          'Growth Gaps/Math/Disability/MAGP'  : '79',
          'Growth Gaps/Math/Disability/MAG'   : 'No',

        'Growth Gaps/Math/LEP'                : '1.5',
          'Growth Gaps/Math/LEP/Eligible'     : '3',
          'Growth Gaps/Math/LEP/Count'        : '81',
          'Growth Gaps/Math/LEP/MGP'          : '57',
          'Growth Gaps/Math/LEP/MAGP'         : '58',
          'Growth Gaps/Math/LEP/MAG'          : 'No',

        # # ===========================================================================
        # # Growth Gaps/Reading
        # # ===========================================================================
        'Growth Gaps/Reading/FRLE': '0',
          'Growth Gaps/Reading/FRLE/Eligible': '3',
          'Growth Gaps/Reading/FRLE/Count': '280',
          'Growth Gaps/Reading/FRLE/MGP': '48',
          'Growth Gaps/Reading/FRLE/MAGP': '61',
          'Growth Gaps/Reading/FRLE/MAG': 'No',

        'Growth Gaps/Reading/Minority': '3',
          'Growth Gaps/Reading/Minority/Eligible': '3',
          'Growth Gaps/Reading/Minority/Count': '628',
          'Growth Gaps/Reading/Minority/MGP': '54',
          'Growth Gaps/Reading/Minority/MAGP': '49',
          'Growth Gaps/Reading/Minority/MAG': 'Yes',

        'Growth Gaps/Reading/Disability': '0',
          'Growth Gaps/Reading/Disability/Eligible': '2',
          'Growth Gaps/Reading/Disability/Count': '95',
          'Growth Gaps/Reading/Disability/MGP': '45',
          'Growth Gaps/Reading/Disability/MAGP': '96',
          'Growth Gaps/Reading/Disability/MAG': 'No',

        'Growth Gaps/Reading/LEP': '0',
          'Growth Gaps/Reading/LEP/Eligible': '3',
          'Growth Gaps/Reading/LEP/Count': '81',
          'Growth Gaps/Reading/LEP/MGP': '49',
          'Growth Gaps/Reading/LEP/MAGP': '82',
          'Growth Gaps/Reading/LEP/MAG': 'No',

        # ===========================================================================
        # Other Factors
        # ===========================================================================
        'Other Factors/Avg. Daily Attendance': '2',
        'Other Factors/Avg. Daily Attendance/Eligible': '2',
        'Other Factors/Avg. Daily Attendance/Rate 2010-2011': '95.90%',

        'Other Factors/6th Grade Drop Out Rate': '1',
        'Other Factors/6th Grade Drop Out Rate/Eligible': '1',
        'Other Factors/6th Grade Drop Out Rate/Rate 2010-2011': '2.00%',

        'Other Factors/7th Grade Drop Out Rate': '1',
        'Other Factors/7th Grade Drop Out Rate/Eligible': '1',
        'Other Factors/7th Grade Drop Out Rate/Rate 2010-2011': '0.90%',

        'Other Factors/Student Overall Positive': '0',
        'Other Factors/Student Overall Positive/Eligible': '1',
        'Other Factors/Student Overall Positive/Count': '7',
        'Other Factors/Student Overall Positive/Rate 2010-2011': '74.69%',

        'Other Factors/LEP/Count': '35',

        'Other Factors/LEP (>24pt gain)': '0',
        'Other Factors/LEP (>24pt gain)/Eligible': '0.5',
        'Other Factors/LEP (>24pt gain)/Rate 2010-2011': '28.57%',
        'Other Factors/LEP (>24pt gain)/Rate 2009-2010': '31.43%',

        'Other Factors/LEP (Attain lvl 5)': '0.5',
        'Other Factors/LEP (Attain lvl 5)/Eligible': '0.5',
        'Other Factors/LEP (Attain lvl 5)/Rate 2010-2011': '40.00%',
        'Other Factors/LEP (Attain lvl 5)/Rate 2009-2010': '25.71%',

        'Other Factors/IEP': '1',
        'Other Factors/IEP/Eligible': '1',
        'Other Factors/IEP/Count': '117',

        'Other Factors/IEP (gte 80 pct)/Rate 2010-2011': '69.23%',
        'Other Factors/IEP (gte 80 pct)/Rate 2009-2010': '62.02%',

        'Other Factors/IEP (Gen Ed)/Rate 2010-2011': '80.04%',
        'Other Factors/IEP (Gen Ed)/Rate 2009-2010': '78.37%',

        'Other Factors/Algebra I Enrollment': '0',
        'Other Factors/Algebra I Enrollment/Eligible': '1',
        'Other Factors/Algebra I Enrollment/Count': '634',
        'Other Factors/Algebra I Enrollment/Rate 2010-2011': '20.66%',
        'Other Factors/Algebra I Enrollment/Rate 2009-2010': '21.37%',

        'Other Factors/Accelerated Course Enrollment': '1',
        'Other Factors/Accelerated Course Enrollment/Eligible': '1',
        'Other Factors/Accelerated Course Enrollment/Count': '1781',
        'Other Factors/Accelerated Course Enrollment/Rate 2010-2011': '68.89%',
        'Other Factors/Accelerated Course Enrollment/Rate 2009-2010': '68.12%',

        # 'Other Factors/6th Grade': '0',
        #   'Other Factors/6th Grade/Eligible': '2',
        #   'Other Factors/6th Grade/Count': '145',
        #   'Other Factors/6th Grade/Rate 2010-2011': '33.10%',
        #   'Other Factors/6th Grade/Rate 2009-2010': '35.33%',

        # 'Other Factors/Student Survey Positive': '1',
        #   'Other Factors/Student Survey Positive/Eligible': '1',
        #   'Other Factors/Student Survey Positive/Count': '36',
        #   'Other Factors/Student Survey Positive/Rate 2010-2011': '96.03%',

        'Other Factors/Parent Engagement Plan': '3',
        'Other Factors/Parent Engagement Plan/Eligible': '3',
    },

    'xml/MS/336-Swainston, Theron L MS.xml': {
        'Other Indicators'     : '5.5',
    },

    # test whole numbers
    'xml/MS/611-Hughes, Charles Arthur MS.xml': {
        'Other Indicators'     : '9',
    },

    'xml/MS/231-Fremont, John C Professional Development MS.xml': {
        'Academic Achievement/Reading/Keep Up': '0',
    },
}

config = SafeConfigParser()
config.optionxform = lambda value: value

def check_school_values(fname, config):
    if 'ES.xml' in fname:
        correct_values = ELEMENTARY_SCHOOL_POINTS.get(fname)
    elif 'MS.xml' in fname:
        correct_values = MIDDLE_SCHOOL_POINTS.get(fname)

    info = extract_from_pdf(fname, config)

    for key in correct_values.iterkeys():
        assert_string = "got: %r, correct: %r for key: %r" % (info[key], correct_values[key], key)
        assert info[key] == correct_values[key], assert_string

def test_elementary_school():
    config.read(['es-config.ini'])
    for fname in ELEMENTARY_SCHOOL_POINTS.iterkeys():
        yield check_school_values, fname, config

def test_middle_school():
    config.read(['ms-config.ini'])
    for fname in MIDDLE_SCHOOL_POINTS.iterkeys():
        yield check_school_values, fname, config
