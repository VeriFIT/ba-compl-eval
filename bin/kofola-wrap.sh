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

# Remove any parameter that contains --high, --check, or --check-det (kofola doesn't accept them)
kofola_params=()
has_high=0
has_check=0
has_check_det=0
for p in "${params[@]}"; do
    if [[ "$p" == *--high* ]]; then
        has_high=1
        # skip this parameter when invoking kofola
        continue
    fi
    # --check-det has to be tested before --check (it contains it as a substring)
    if [[ "$p" == *--check-det* ]]; then
        has_check_det=1
        # skip this parameter when invoking kofola
        continue
    fi
    if [[ "$p" == *--check* ]]; then
        has_check=1
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

TIMEOUT=100
AUTCROSS_CMD="autcross"

# Compares the obtained automaton (${TMP}) with the automaton produced by the
# reference command given as the first argument (a shell command using the
# autcross placeholders %H and %O). The verdict (True/False/TO/NA) is stored
# in CHECK_RESULT.
check_against() {
    local reference="$1"
    local CHECK_TMP=$(mktemp)

    cat "${INPUT}" | timeout ${TIMEOUT} ${AUTCROSS_CMD} "a=%H; cat ${TMP} > %O" "${reference}" > "${CHECK_TMP}" 2>&1

    local check_ret=$?
    if [ ${check_ret} -eq 0 ]; then
        CHECK_RESULT="True"
    elif [ ${check_ret} -eq 124 ]; then
        CHECK_RESULT="TO"
    elif grep -q "Too many acceptance sets used." "${CHECK_TMP}"; then
        CHECK_RESULT="NA"
    elif grep -q "both automata accept the infinite word" "${CHECK_TMP}"; then
        CHECK_RESULT="False"
    else
        CHECK_RESULT="NA"
    fi

    rm -f "${CHECK_TMP}"
}

# Checks whether all the automata in ${TMP} are deterministic; the verdict
# (True/False/NA) is stored in DET_RESULT.
check_deterministic() {
    local num_aut=$(autfilt --count "${TMP}" 2>/dev/null)
    local num_det=$(autfilt --count --is-deterministic "${TMP}" 2>/dev/null)

    if [ -z "${num_aut}" ] || [ "${num_aut}" -eq 0 ]; then
        DET_RESULT="NA"
    elif [ "${num_aut}" -eq "${num_det}" ]; then
        DET_RESULT="True"
    else
        DET_RESULT="False"
    fi
}

# if --check is specified, check correctness of the complementation using autcross
if [ "$has_check" -eq 1 ]; then
    check_against 'autfilt --complement %H > %O'
    echo "check: ${CHECK_RESULT}"
fi

# if --check-det is specified, check that the result is a correctly determinised
# automaton, i.e., (i) it is equivalent to the input and (ii) it is deterministic.
# "check" gives the overall verdict (as for --check), "det" the determinism alone.
if [ "$has_check_det" -eq 1 ]; then
    # (i) equivalence with the input automaton (the reference tool is the identity)
    check_against 'autfilt %H > %O'
    # (ii) determinism of the result
    check_deterministic

    # the overall verdict is True only if the language is right AND the result
    # is deterministic (DET_RESULT is False or NA in the branch below)
    if [ "${CHECK_RESULT}" == "True" ] && [ "${DET_RESULT}" != "True" ]; then
        CHECK_RESULT="${DET_RESULT}"
    fi

    echo "check: ${CHECK_RESULT}"
    echo "det: ${DET_RESULT}"
fi

rm -f "${TMP}"

exit ${ret}
