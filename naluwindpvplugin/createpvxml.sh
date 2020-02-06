#!/bin/sh

embedpythonfile=embedpython.py
templatefile=nalusource3.template.xml
outfile=naluwindplugin.xml

# Read the python file and replace newlines
embedpython=`sed ':a;N;$!ba;s/\n/\\\\\&#xa;/g' $embedpythonfile`

sed "s|REPLACEPYTHON|$embedpython|g" $templatefile > $outfile
