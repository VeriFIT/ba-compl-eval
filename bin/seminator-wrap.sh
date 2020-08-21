#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

INPUT=$1
shift
params="$*"

TMP=$(mktemp)
./util/ba2hoa.py ${INPUT} > ${TMP} || exit $?

out=$(./bin/seminator --complement --ba ${params} ${TMP} | grep "^States:")
ret=${PIPESTATUS[0]}
rm ${TMP}

echo ${out}

exit ${ret}
