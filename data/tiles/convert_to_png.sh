#!/bin/bash

OUT=./png/

echo "Creating $OUT"
mkdir -p $OUT

find ./ecw/ -name "*.ecw" -print0 | while read -d $'\0' FILE
do
    echo $FILE
    TARGET=$( echo $FILE | cut -d "/" -f 4)
    TARGET=${TARGET/.ecw/.png}
    echo $TARGET

    gdal_translate -of PNG $FILE $OUT/$TARGET
done

# find . -name "*.ecw" | xargs -P 16 -l bash -c 'gdal_translate $0 ./tif/$( echo ${0/.ecw/.tif} | cut -d "/" -f 3)'