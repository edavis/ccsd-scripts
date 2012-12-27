#!/usr/bin/env python

import re
import os
import redis
import pprint
import tablib
import hashlib
import operator
import Image, ImageOps
from collections import defaultdict
from operator import itemgetter
from configparser import ConfigParser, ExtendedInterpolation

IMAGE_CACHE = {'active': None, 'im': None}
COMMON_TRANSLATIONS = {'O': '0', '_': '-'}

redis_conn = redis.StrictRedis()

def coords(coord):
    """
    Translate (x, y) coordinates along with (width, height)
    measurements into a box used to crop the TIFF image.

    >>> coords('615,158 32,24')
    (615, 158, 615+32, 158+24)
    """
    x, y, w, h = re.search('^(\d+),(\d+)[ ,](\d+),(\d+)$', coord).groups()
    x, y, w, h = map(int, [x, y, w, h])
    return (x, y, x+w, y+h)

def extract_region(image, coordinates):
    """
    Crop the given image using the given coordinates into output file.
    """
    output = hashlib.md5(image + coordinates).hexdigest()
    output = os.path.join('regions', output + '.tiff')
    if not os.path.exists(output):
        print("extracting_region(%r, %r)" % (image, coordinates))
        print(" -> '%s'" % output)
        # Cache the Image object to speed things up.
        #
        # This way, we only open an original image up once and crop as
        # many times as needed -- rather than opening the same
        # original image a bunch of times.
        #
        # We only store the active Image object and discard it once we
        # move onto the next image to keep the cache from growing too
        # big. Since we only open image files once, this isn't a huge
        # deal.
        if not IMAGE_CACHE['active'] == image:
            IMAGE_CACHE['active'] = image
            IMAGE_CACHE['im'] = Image.open(image)
        im = IMAGE_CACHE['im']
        box = coords(coordinates)
        region = im.crop(box)
        pix = region.load()
        # If the top-leftmost pixel isn't white, coerce to black and white.
        if pix[0,0] != (255, 255, 255):
            region = ImageOps.grayscale(region)
            # http://stackoverflow.com/questions/6485254/how-to-i-use-pil-image-pointtable-method-to-apply-a-threshold-to-a-256-gray-im
            region = region.point(lambda p: p > 50 and 255)
        region.save(output)
    return output

def extract_text(region):
    """
    Return a given region's text via OCR.
    """
    if not redis_conn.exists(region):
        cmd = "tesseract {} {} -psm 7 &>/dev/null"
        os.system(cmd.format(region, "output"))

        with open("output.txt") as fp:
            content = fp.read().strip()
            content = COMMON_TRANSLATIONS.get(content, content)

        redis_conn.set(region, content)
        return content
    else:
        return redis_conn.get(region)

def build_config(config_file):
    """
    Build a ConfigParser object.

    Two notes:
    - Use ExtendedInterpolation
    - Don't downcase key names
    """
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.optionxform = lambda opt: opt
    config.read([config_file])
    return config

def get_tiff_files(tiff_dir):
    """
    >>> result = get_tiff_files('tiff/')
    >>> result[0]
    '245-Mojave HS'
    >>> result[1]
    {1: '/path/to/tiff/245-Mojave HS/page_01.tiff', 2: ...}
    """
    for school in os.listdir(tiff_dir):
        full_tiff_dir = os.path.abspath(os.path.join(tiff_dir, school))
        tiff_files = {n: os.path.join(full_tiff_dir, 'page_%02d.tiff' % n) for n in xrange(1, 5)}
        yield (school, tiff_files)

def write_to_csv(results, output):
    """
    Create a CSV file of results in output.
    """
    data = tablib.Dataset(headers=[])
    for (school, sections) in sorted(results.iteritems(), key=operator.itemgetter(0)):
        school_values = {}
        for (section, values) in sections.iteritems():
            for (key, value) in values.iteritems():
                school_values['/'.join([section, key])] = value

        school_values = sorted(school_values.iteritems(), key=operator.itemgetter(0))
        data.append([school] + [value for key, value in school_values])
        if not data.headers:
            headers = [key for key, value in school_values]
            headers.insert(0, 'school')
            data.headers = headers

    with open(output, 'wb') as fp:
        fp.write(data.csv)

def display_summary(results, args):
    """
    Display a summary of the results.

    With only a 'school' argument provided, display all values from
    that school.

    If a 'section' argument is provided, display values matching that
    section regex.
    """
    if args.school:
        for school, sections in results.iteritems():
            if args.school and (not re.search(args.school, school)):
                continue
            for (section, values) in sorted(sections.iteritems(), key=itemgetter(0)):
                if args.section and (not re.search(args.section, section)):
                    continue
                print("Section: {}".format(section))
                pprint.pprint(dict(values))
                print("")

def main(args):
    config = build_config(args.config)
    results = {}

    for school, tiff_files in get_tiff_files(args.tiff_dir):
        # if --school given, parse on that school
        if args.school and (not re.search(args.school, school)):
            continue

        print("Processing '{}'".format(school))
        results[school] = defaultdict(dict)

        for section in config.sections():
            if section == 'pages':
                continue

            if '/' in section:
                main_section = section.split('/')[0]
            else:
                main_section = section

            page = int(config['pages'].get(main_section))
            active_image = tiff_files[page]
            results[school][section] = defaultdict(dict)

            for (option_key, option_value) in config[section].items():
                region = extract_region(active_image, option_value)
                text = extract_text(region)
                results[school][section][option_key] = text

    display_summary(results, args)
    write_to_csv(results, args.output)

if __name__ == "__main__":
    if not os.path.exists('regions'):
        os.mkdir('regions')

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-t', '--tiff-dir')
    parser.add_argument('-s', '--section')
    parser.add_argument('--school')
    parser.add_argument('-o', '--output', default='output.csv')
    args = parser.parse_args()
    main(args)
