#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

INPUT=$1
shift
params="$*"

GOAL_DIR=./bin/goal

GOAL_TMP_DIR="$(mktemp -d)"
cp -r ${GOAL_DIR} ${GOAL_TMP_DIR}

TMP="$(mktemp).gff"
./util/ba2gff.py ${INPUT} > ${TMP} || exit $?

TIME_TMP="$(mktemp)"
set -o pipefail
# out=$(time ${GOAL_TMP_DIR}/goal/gc complement ${params} ${TMP} ${TIME_TMP} | grep -i "<state sid" | wc -l)
out=$(/usr/bin/time -p ${GOAL_TMP_DIR}/goal/gc complement ${params} ${TMP} 2>${TIME_TMP} | grep -i "<state sid" | wc -l)
ret=$?
rm ${TMP}
rm -rf ${GOAL_TMP_DIR}

echo "States: ${out}"
cat ${TIME_TMP} | grep "user" | sed "s/user/Time:/"

exit ${ret}
