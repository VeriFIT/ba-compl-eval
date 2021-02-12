#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) ] ; then
	echo "usage: ${0} <input-ba>"
	exit 1
fi

INPUT=$1
BASEN="$(dirname ${INPUT})/$(basename -s .hoa ${INPUT})"

j=1
OUTFILE="${BASEN}-${j}.hoa"
echo ${OUTFILE}
cat ${INPUT} | while read line ; do
	if [ -z "${line}" ] ; then
		j=$((j+1))
		OUTFILE="${BASEN}-${j}.hoa"
		echo ${OUTFILE}
	else
		echo "${line}" >> ${OUTFILE}
	fi
done
