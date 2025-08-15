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

# Remove any parameter that contains --high (kofola doesn't accept it)
kofola_params=()
has_high=0
for p in "${params[@]}"; do
    if [[ "$p" == *--high* ]]; then
        has_high=1
        # skip this parameter when invoking kofola
        continue
    fi
    kofola_params+=("$p")
done

kofola_exe="${SCRIPT_DIR}/kofola/build/src/kofola"
# capture the full version string (may contain spaces)
kofola_version_string="$("${kofola_exe}" --version 2>/dev/null)"
# extract the last whitespace-separated token (the git hash)
kofola_git_hash=$(awk '{print $NF}' <<< "${kofola_version_string}")
kofola_str=${kofola_git_hash:0:7}

TMP=$(mktemp)

# make sure pipeline failures are detected
set -o pipefail

if [ "$has_high" -eq 1 ]; then
    "${kofola_exe}" "${kofola_params[@]}" "${INPUT}" | autfilt --high > "${TMP}"
else
    "${kofola_exe}" "${kofola_params[@]}" "${INPUT}" > "${TMP}"
fi

# capture return code
ret=$?

# prefix the States header with the short git hash and print the full output
cat "${TMP}" | grep "^States:" | sed "s/^States/$kofola_str-states/"

rm -f "${TMP}"

exit ${ret}
