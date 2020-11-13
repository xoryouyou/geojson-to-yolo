#!/bin/bash

OUT=./tif/

# echo "Creating $OUT"
mkdir -p $OUT

find . -name "*.ecw" -print0 | while read -d $'\0' FILE
do
    TARGET=$( echo $FILE | cut -d "/" -f 4)
    TARGET=${TARGET/.ecw/.tif}
    

    echo "gdal_translate $FILE $OUT/$TARGET"
done

# >> jobs.txt
# cat jobs.txt | parallel -j 32  

# find . -name "*.ecw" | xargs -P 16 -l bash -c 'gdal_translate $0 ./tif/$( echo ${0/.ecw/.tif} | cut -d "/" -f 3)'