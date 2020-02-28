#!/bin/sh

embedpythonfile=embedPlotPlane.py
embedreqinfofile=embedRequestInfoTimesteps.py
templatefile=sampleplane.template.xml
outfile=sampleplaneplugin.xml

# Read the python file and replace newlines
embedpython=`sed -e ':a;N;$!ba;s/\n/\\\\\&#xa;/g'  $embedpythonfile`
embedreqinfo=`sed ':a;N;$!ba;s/\n/\\\\\&#xa;/g' $embedreqinfofile`
sed -e "s|REPLACESAMPLEPYTHON|$embedpython|g" \
    -e "s|REPLACEREQUESTINFO|$embedreqinfo|g" \
    $templatefile > $outfile
