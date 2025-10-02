#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 2 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

A=$1
B=$2
shift
shift
params=("$@")

ABSOLUTE_SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "${ABSOLUTE_SCRIPT_PATH}")

bait_exe="java -jar ${SCRIPT_DIR}/BAIT/bait.jar"
bait_str="bait"

TMP=$(mktemp)
${bait_exe} "$A" "$B" "${params[@]}" > "${TMP}"
ret=$?

# print result flag based on exit code while preserving the original exit code
if [ "${ret}" -eq 0 ]; then
	echo "${bait_str}-result: true"
elif [ "${ret}" -eq 1 ]; then
	echo "${bait_str}-result: false"
else 
	echo "${bait_str}-result: `cat ${TMP}`"
fi

rm ${TMP}
exit 0