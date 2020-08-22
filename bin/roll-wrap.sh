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

set -o pipefail
out=$(java -jar ./bin/ROLL.jar complement ${TMP} -v 0 -table -syntactic ${params} | grep '#H.S' | sed -E 's/^.*([0-9]+).*$/\1/')
ret=$?
rm ${TMP}

echo "States: ${out}"

exit ${ret}
