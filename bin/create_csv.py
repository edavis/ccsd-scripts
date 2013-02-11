#!/usr/bin/env python

import re
import tablib
import pymongo
import operator
from ocr_pdf import build_config, get_current_year
from collections import defaultdict
import decimal

conn = pymongo.Connection()
db = conn.ccsd
ccsd = db.ccsd

def get_section(school_type, section):
    return ccsd.find({
        'school.type': school_type,
        'section': section,
        'year': get_current_year(),
    })

def section_to_dict(it):
    ret = defaultdict(dict)
    for item in it:
        school = item.get('school')
        school_name = school.get('name')
        category = item.get('category')
        value = item.get('value')
        ret[school_name][category] = value
    return ret

def get_compare_function(section, config):
    lookup = config.options(section)

    def _cmp(x, y):
        x = lookup.index(x)
        y = lookup.index(y)
        return -1 if (x < y) else (1 if y > x else 0)

    return _cmp

def add_extra(categories, value):
    value = re.sub('^! *', '', value)
    new_categories = {}

    for key, category_value in categories.iteritems():
        new = re.sub('[%/ ()-]', '_', key).lower()
        new = re.sub('__+', '_', new)
        new = re.sub('_-_', '_', new) # for IEP/LEP
        new = re.sub('_$', '', new)

        if category_value.isdigit():
            category_value = int(category_value)

        elif '%' in category_value:
            category_value = category_value.replace('%', '')
            category_value = decimal.Decimal(category_value) / decimal.Decimal('100')

        new_categories[new] = category_value

    try:
        with decimal.localcontext() as ctx:
            ctx.prec = 4
            return eval(value, new_categories)
    except (TypeError, decimal.InvalidOperation, decimal.DivisionByZero,
            ZeroDivisionError):
        return ''
    except Exception:
        raise

def dict_to_dataset(ret, section, config):
    data = tablib.Dataset()
    compare_function = get_compare_function(section, config)

    for school, categories in sorted(ret.iteritems(), key=operator.itemgetter(0)):
        if not data.headers:
            data.headers = ['School'] + sorted(categories.iterkeys(), cmp=compare_function)

        row = [school]
        for label, value in sorted(categories.iteritems(),
                                   key=operator.itemgetter(0),
                                   cmp=compare_function):
            if value.startswith('!'):
                value = add_extra(categories, value)

            row.append(value)
        data.append(row)
    return data

def write_csv(args):
    config = build_config(args.config)
    datasets = []

    for section in config.sections():
        it = get_section(args.school_type, section)
        ret = section_to_dict(it)
        dataset = dict_to_dataset(ret, section, config)
        datasets.append(dataset)

    with open(args.output, 'wb') as fp:
        for dataset in datasets:
            fp.write(dataset.csv + '\n')

    return args.output

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--school-type')
    parser.add_argument('-c', '--config')
    parser.add_argument('-o', '--output')
    write_csv(parser.parse_args())

if __name__ == "__main__":
    main()
