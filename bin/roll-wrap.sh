#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

INPUT=$1
shift
params="$*"

TMP="$(mktemp).hoa"
./util/ba2hoa.py ${INPUT} > ${TMP} || exit $?

# out=$(java -jar bin/ROLL.jar complement -v 0 -table -syntactic ${params} ${TMP} | grep "^States:")
out=$(java -jar ./bin/ROLL.jar complement ${TMP} -v 0 -table -syntactic ${params} | grep '#H.S' | sed -E 's/^.*([0-9]+).*$/\1/')
ret=${PIPESTATUS[0]}
rm ${TMP}

echo "States: ${out}"

exit ${ret}
