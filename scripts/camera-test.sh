#!/bin/sh
#

#
# :title Camera Test
# :content-type .
#
# :checkbox test 1 640x480 Test picture
# :label width Width:
# :text width --pattern=^[0-9]+$ 3280
# :label height Height:
# :text height --pattern=^[0-9]+$ 2464
# :label iso ISO:
# :select iso :auto, 100, 200:200, 400, 800
# :label shutter Shutter speed (ms, max 6000000):
# :text shutter --max=8000000 --pattern=^[0-9]+$ 100
# :label rot Rotation:
# :select rot :none, 270:rotate left, 90:rotate right
#

dir=`dirname "$PATH_TRANSLATED"`
filename=$dir/image.jpg

if [ "$CGI_TEST" = "1" ]; then
    CGI_WIDTH=640
    CGI_HEIGHT=480
fi

if [ "$CGI_SHUTTER" != ""  -a  "$CGI_SHUTTER" != 0 ]; then
    OPT="$OPT --shutter $CGI_SHUTTER"
fi

raspistill -w "$CGI_WIDTH" -h "$CGI_HEIGHT" -rot "$CGI_ROT" \
	$OPT \
	-q 100 -t 500 -ae 511 -sh 100 \
	-o $filename

echo Status: 200
echo Filename: $filename
echo

