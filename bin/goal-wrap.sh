#!/bin/bash

# Check the number of command-line arguments
if [ \( "$#" -lt 1 \) ] ; then
	echo "usage: ${0} <input-ba> [<params>]"
	exit 1
fi

INPUT=$1
shift
params="$*"

TMP="$(mktemp).gff"
./util/ba2gff.py ${INPUT} > ${TMP}

out=$(bin/goal/gc complement ${params} ${TMP} | grep -i "<state sid" | wc -l)
ret=$?
rm ${TMP}

echo "States: ${out}"

exit ${ret}

# lockdir=/tmp/goal.lock
# while true ; do
	# if mkdir "$lockdir" ; then    # directory did not exist, but was created successfully
		# trap 'rm -rf "$lockdir"' 0    # remove directory when script finishes
#
		# TMP="$(mktemp).gff"
		# ./util/ba2gff.py ${INPUT} > ${TMP}
#
		# out=$(bin/goal/gc complement ${params} ${TMP} | grep -i "<state sid" | wc -l)
		# ret=$?
		# rm ${TMP}
#
		# echo "States: ${out}"
#
		# exit ${ret}
	# else
    # echo "Waiting..."
		# sleep 1          # wait
	# fi
# done
