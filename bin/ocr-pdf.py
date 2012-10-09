#!/usr/bin/env python

import re
import os
import glob
import pprint
import hashlib
import Image, ImageOps
from collections import defaultdict
from operator import itemgetter
from configparser import ConfigParser, ExtendedInterpolation

IMAGE_CACHE = {'active': None, 'im': None}
COMMON_TRANSLATIONS = {'O': '0', '_': '-'}

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
    (base, ext) = os.path.splitext(region)
    txt = base + '.txt'
    if not os.path.exists(txt):
        cmd = "tesseract {} {} -psm 7 &>/dev/null"
        os.system(cmd.format(region, base))

    with open(txt) as fp:
        content = fp.read().strip()
        return COMMON_TRANSLATIONS.get(content, content)

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
    {1: 'tiff/245-Mojave HS/page_01.tiff', 2: ...}
    """
    for school in os.listdir(tiff_dir):
        full_tiff_dir = os.path.join(tiff_dir, school)
        tiff_files = {n: os.path.join(full_tiff_dir, 'page_%02d.tiff' % n) for n in xrange(1, 5)}
        yield (school, tiff_files)

def main(args):
    config = build_config(args.config)
    results = {}

    for school, tiff_files in get_tiff_files(args.tiff_dir):
        if args.school and (not re.search(args.school, school)):
            continue

        print("Processing '{}'".format(school))
        results[school] = defaultdict(dict)

        for section in config.sections():
            if section == 'pages':
                continue

            page = int(config[section].get('page'))
            active_image = tiff_files[page]
            results[school][section] = defaultdict(dict)

            for (option_key, option_value) in config[section].items():
                if option_key == 'page':
                    continue

                region = extract_region(active_image, option_value)
                text = extract_text(region)
                results[school][section][option_key] = text

    if args.school:
        for school, sections in results.iteritems():
            if args.school and (not re.search(args.school, school)):
                continue
            for (section, values) in sections.iteritems():
                if args.section and (not re.search(args.section, section)):
                    continue
                print("Section: {}".format(section))
                pprint.pprint(dict(values))
                print("")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-t', '--tiff-dir')
    parser.add_argument('-s', '--section')
    parser.add_argument('--school')
    args = parser.parse_args()
    main(args)
