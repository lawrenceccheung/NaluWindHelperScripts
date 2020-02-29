#!/bin/sh


embedpythonfile=embedpython.py                   # For the yaml domain plugin
embedSPpythonfile=embedPlotPlane.py              # For the sample plane plugin
embedreqinfofile=embedRequestInfoTimesteps.py    # For the sample plane plugin


templatefile=plugin.template.xml
outfile=naluwindplugin.xml

# Read the python file and replace newlines
embedpython=`sed ':a;N;$!ba;s/\n/\\\\\&#xa;/g' $embedpythonfile`
embedSPpython=`sed -e ':a;N;$!ba;s/\n/\\\\\&#xa;/g'  $embedSPpythonfile`
embedreqinfo=`sed ':a;N;$!ba;s/\n/\\\\\&#xa;/g'      $embedreqinfofile`

# Now insert python into xml file
sed -e "s|REPLACEPYTHON|$embedpython|g"       \
    -e "s|REPLACESAMPLEPYTHON|$embedSPpython|g" \
    -e "s|REPLACEREQUESTINFO|$embedreqinfo|g" \
    $templatefile > $outfile
