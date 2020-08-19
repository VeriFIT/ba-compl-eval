#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) ] ; then
	echo "usage: ${0} <input-ba>"
	exit 1
fi

INPUT=$1
TMP=$(mktemp)
util/ba2hoa.py ${INPUT} > ${TMP}
out=$(bin/seminator --complement ${TMP} | grep "^States:")
ret=$?
rm ${TMP}
echo ${out}

exit ${ret}
