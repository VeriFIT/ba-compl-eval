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

autfilt_exe="autfilt"
# capture the full version output (may contain multiple lines)
autfilt_version_output="$("${autfilt_exe}" --version 2>/dev/null)"
# extract the first line
autfilt_first_line=$(awk 'NR==1{print; exit}' <<< "${autfilt_version_output}")
# extract the version token from the first line (last whitespace-separated field)
autfilt_version=$(awk '{print $NF}' <<< "${autfilt_first_line}")
autfilt_str=${autfilt_version}

TMP=$(mktemp)
"${autfilt_exe}" --included-in="$B" "$A" "${params[@]}" > "${TMP}"
ret=$?

# print result flag based on exit code while preserving the original exit code
if [ "${ret}" -eq 0 ]; then
	echo "${autfilt_str}-result: true"
elif [ "${ret}" -eq 1 ]; then
	echo "${autfilt_str}-result: false"
fi

rm ${TMP}

exit 0