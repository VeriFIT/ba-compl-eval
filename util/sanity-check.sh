#!/bin/bash

HELP_MSG="usage: ${0} <input-ba> [--all]"
TIMEOUT=60
AUTCROSS_CMD="autcross -T ${TIMEOUT}"

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) -o \( "$#" -gt 2 \) ] ; then
	echo ${HELP_MSG}
	exit 1
fi

if [ \( "$#" -eq 2 \) -a \( "$2" != "--all" \) ] ; then
	echo ${HELP_MSG}
	exit 1
fi

INPUT=$1
ALL=0
if [ \( "$#" -eq 2 \) -a \( "$2" == "--all" \) ] ; then
	ALL=1
fi

if [ \( ${ALL} == 1 \) ] ; then
	cat ${INPUT} | ${AUTCROSS_CMD} \
	'./bin/autfilt --complement %H >%O' \
	'./bin/ranker %H >%O' \
	'./bin/seminator --complement %H >%O' \
	'./bin/ltl2dstar --complement-input=yes --input=nba --output=nba -H %H %O' \
	'./bin/roll-autcross-wrap.sh %H %O' \
	'./bin/goal-autcross-wrap.sh %H %O -m safra' \
	'./bin/goal-autcross-wrap.sh %H %O -m piterman' \
	'./bin/goal-autcross-wrap.sh %H %O -m rank -tr -ro' \
	'./bin/goal-autcross-wrap.sh %H %O -m fribourg' \
	'./bin/ranker-tight %H >%O' \
	'./bin/ranker-composition %H >%O'
else
	cat ${INPUT} | ${AUTCROSS_CMD} \
		'./bin/autfilt --complement %H >%O' \
		'./bin/ranker %H >%O'
fi
