#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) ] ; then
	echo "usage: ${0} <input-ba>"
	exit 1
fi

INPUT=$1
TMP="$(mktemp).gff"
./util/ba2gff.py ${INPUT} > ${TMP}

out=$(bin/goal/gc complement -m safra ${TMP} | grep -i "<state sid" | wc -l)
ret=$?
rm ${TMP}

echo "States: ${out}"

exit ${ret}
