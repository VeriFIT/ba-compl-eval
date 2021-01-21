#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) ] ; then
	echo "usage: ${0} <input-file>"
	exit 1
fi
INPUT=$1

util/classify_ba.sh --print-header
j=1
cat ${INPUT} | while read line ; do
	printf "$j: classifying ${line}...\n" >&2
	util/classify_ba.sh --csv $line
	j=$((j+1))
done
