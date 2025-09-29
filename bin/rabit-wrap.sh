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

rabit_exe="java -jar ${SCRIPT_DIR}/rabit/RABIT.jar"
rabit_str="rabit"

TMP=$(mktemp)
${rabit_exe} "$A" "$B" "${params[@]}" > "${TMP}"
ret=$?

# read temporary output and interpret known messages
result_text=$(cat "${TMP}")

# If the tool prints an explicit inclusion/exclusion message prefer that over exit code
if echo "${result_text}" | grep -qF "Not included."; then
	echo "${rabit_str}-result: false"
elif echo "${result_text}" | grep -qF "Included"; then
	echo "${rabit_str}-result: true"
else
	echo "${rabit_str}-result: ${result_text}"
fi

rm ${TMP}
exit 0