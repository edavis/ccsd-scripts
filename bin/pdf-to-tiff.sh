#!/bin/bash

set -e

for pdf in pdf/*.pdf; do
    base=`gbasename -s .pdf "$pdf"`
    out_base="tiff/$base"
    mkdir -p "$out_base"
    output="$out_base/page_%02d.tiff"
    gs -o "$output" -sDEVICE=tiffgray -r720x720 \
        -sCompression=lzw "$pdf"
done
