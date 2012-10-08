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
        return {'O': '0', '_': '-'}.get(content, content)

def main(args):
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.optionxform = lambda opt: opt
    config.read([args.config])

    log = open('output.log', 'w')
    results = {}

    for tiff_dir in os.listdir(args.tiff_dir):
        tiff_dir = os.path.join(args.tiff_dir, tiff_dir)
        tiff_files = sorted(glob.glob(tiff_dir + '/*.tiff'))
        tiff_files = {idx+1: tiff for (idx, tiff) in enumerate(tiff_files)}

        tiff_dir_basename = os.path.basename(tiff_dir)
        results[tiff_dir_basename] = defaultdict(dict)

        print tiff_dir_basename

        for section in config.sections():
            if section == 'pages':
                continue

            page = int(config[section].get('page'))
            active_image = tiff_files[page]
            results[tiff_dir_basename][section] = defaultdict(dict)

            for (option_key, option_value) in config[section].items():
                if option_key == 'page':
                    continue

                region = extract_region(active_image, option_value)
                text = extract_text(region)
                results[tiff_dir_basename][section][option_key] = text

    results = sorted(results.iteritems(), key=itemgetter(0))
    for school, values in results:
        print '--> {} <--'.format(school)
        pprint.pprint(dict([category, dict(e)] for category, e in values.items()))

        # for section in config.sections():
        #     options = dict(config.items(section))
        #     page = int(options.pop('page'))
        #     active_page = tiff_files[page]

        #     print "--> %s" % active_page
        #     log.write("--> %s\n" % active_page)

        #     for (key, coordinates) in sorted(options.items()):
        #         region = extract_region(active_page, coordinates)
        #         text = extract_text(region)
        #         info = (region, key, text) if args.verbose else (key, text)
        #         log.write(repr(info) + '\n')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-t', '--tiff-dir')
    parser.add_argument('-o', '--output')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    main(args)
