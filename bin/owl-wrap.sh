#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

ABSOLUTE_SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "${ABSOLUTE_SCRIPT_PATH}")

INPUT=$1
shift
# preserve argument boundaries and spacing
params=("$@")

owl_exe="${SCRIPT_DIR}/owl/owl-linux-musl-amd64-21.0/bin/owl"
# capture version output: "owl (version: 21.0)"
owl_version_output="$("${owl_exe}" --version 2>/dev/null)"
# extract version number from "owl (version: X.Y)"
owl_version=$(echo "${owl_version_output}" | grep -oP '(?<=version: )[^\)]+')
owl_str="${owl_version}"

TMP=$(mktemp)
"${owl_exe}" nba2dpa "${params[@]}" -i "${INPUT}" > "${TMP}" || exit 1

autfilt "${TMP}" | grep "^States:" | sed "s/^States/${owl_str}-states/"

rm -f "${TMP}"
