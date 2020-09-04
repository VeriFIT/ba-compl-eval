#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) ] ; then
	echo "usage: ${0} <input-ba>"
	exit 1
fi

INPUT=$1

TMP=$(mktemp)
./util/ba2hoa.py ${INPUT} > ${TMP} || exit $?

TMP_OUT=$(mktemp)
./bin/autfilt --high --ba --split-edges ${TMP} > ${TMP_OUT}

#./bin/goal/gc batch 'load $omega $1; save $omega -c ba $2;' ${TMP_OUT} ${TMP_OUT}

cat ${TMP_OUT} | ./util/hoa2ba.py

rm ${TMP}
rm ${TMP_OUT}
