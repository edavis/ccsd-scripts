#!/bin/bash

set -e

for pdf in pdf/*.pdf; do
    base=`gbasename -s .pdf "$pdf"`
    out_base="tiff/$base"
    mkdir -p "$out_base"
    output="$out_base/page_%02d.tiff"
    if [ ! -f "$out_base/page_01.tiff" ]; then
      echo "--> $base"
      gs -o "$output" -sDEVICE=tiffgray -r720x720 \
          -sCompression=lzw "$pdf"
    fi
done
