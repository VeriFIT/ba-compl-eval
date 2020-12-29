#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 3 \) ] ; then
	echo "usage: ${0} <tool> <input-ba> <output-ba>"
	exit 1
fi

TOOL=$1
INPUT=$2
OUTPUT=$3

${TOOL} ${INPUT} > ${OUTPUT}
