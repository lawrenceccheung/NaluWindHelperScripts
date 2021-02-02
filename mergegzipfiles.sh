#!/usr/bin/sh
#

FILE1=$1
FILE2=$2
OUTFILE=$3

TEMP1=TEMP1.dat
TEMP2=TEMP2.dat
# unzip the files
gzip -dc $FILE1 > $TEMP1
gzip -dc $FILE2 > $TEMP2
paste $TEMP1 $TEMP2 |sed 's/#//g' | sed -e '1s/^/#/' -e '2s/^/#/' > $OUTFILE
rm $TEMP1 $TEMP2


