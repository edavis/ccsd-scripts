#!/usr/bin/env python

import re
import os
import redis
import pprint
import tablib
import hashlib
import pymongo
import operator
import Image, ImageOps
from collections import defaultdict
from operator import itemgetter
from configparser import ConfigParser, ExtendedInterpolation

ccsd_database = pymongo.Connection().ccsd

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
    root = '/var/ccsd-scripts/regions/%s/%s/' % (output[:2], output[2:4])
    if not os.path.isdir(root):
        os.makedirs(root)
    output = os.path.join(root, output + '.tiff')
    if not os.path.exists(output):
        print("extracting_region(%r, %r)" % (image, coordinates))
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
        print("extract_text(%r)" % region)
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

def get_school_type(tiff_files):
    fn = tiff_files[1]
    if '/es/' in fn:
        return 'Elementary'
    elif '/ms/' in fn:
        return 'Middle'
    elif '/hs/' in fn:
        return 'High'

def insert_documents(documents):
    ccsd_database.ccsd.insert(documents, safe=True)

def remove_existing_documents(config):
    school_type = None

    if 'hs.ini' in config:
        school_type = 'High'
    elif 'ms.ini' in config:
        school_type = 'Middle'
    elif 'es.ini' in config:
        school_type = 'Elementary'

    if school_type is not None:
        ccsd_database.ccsd.remove({'school.type': school_type})

def main(args):
    config = build_config(args.config)

    remove_existing_documents(args.config)

    for school, tiff_files in get_tiff_files('tiff'):
        print("Processing '{}'".format(school))
        (school_id, school_name) = school.split('-', 1)

        documents = []
        document = {
            'school': {
                'name': school_name,
                'id': int(school_id),
                'type': get_school_type(tiff_files),
            },
        }

        for section in config.sections():
            (page, section_label) = section.split('-', 1)
            current_image = tiff_files[int(page)]

            for (category, coordinates) in config[section].items():
                text = extract_text(extract_region(current_image, coordinates))
                document['section'] = section
                document['category'] = category
                document['value'] = text
                documents.append(document.copy())

        insert_documents(documents)

if __name__ == "__main__":
    # ccsd_database.ccsd.drop()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    main(args)
