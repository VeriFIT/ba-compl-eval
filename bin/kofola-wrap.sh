#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [params]"
	exit 1
fi

ABSOLUTE_SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "${ABSOLUTE_SCRIPT_PATH}")

INPUT=$1
shift
# preserve argument boundaries and spacing
params=("$@")

kofola_exe="${SCRIPT_DIR}/kofola/build/src/kofola"
# capture the full version string (may contain spaces)
kofola_version_string="$("${kofola_exe}" --version 2>/dev/null)"
# extract the last whitespace-separated token (the git hash)
kofola_git_hash=$(awk '{print $NF}' <<< "${kofola_version_string}")
kofola_str=${kofola_git_hash:0:7}

TMP=$(mktemp)
"${kofola_exe}" "${params[@]}" "${INPUT}" > "${TMP}" || exit 1

set -o pipefail
autfilt_out=$(autfilt --high "${TMP}" | grep "^States:" | sed "s/^States/$kofola_str-autfilt-states/")
ret=$?

cat "${TMP}" | grep "^States:" | sed "s/^States/$kofola_str-states/"
echo "${autfilt_out}"

rm -f "${TMP}"

exit ${ret}
