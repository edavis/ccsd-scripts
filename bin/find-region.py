#!/usr/bin/env python

import os
import hashlib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-c', '--coord')
args = parser.parse_args()

path = os.path.abspath(args.file)
hashed = hashlib.md5(path + args.coord).hexdigest()

print "/var/ccsd-scripts/regions/%s/%s/%s.tiff" % (
    hashed[:2], hashed[2:4], hashed)
