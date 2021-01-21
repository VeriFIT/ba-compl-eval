#!/bin/bash
AUTFILT="autfilt"

# Check the number of command-line arguments
if [ \( "$#" -ne 1 \) -a \( "$#" -ne 2 -o "$1" != "--csv" \) ] ; then
	echo "usage: ${0} [--csv] <input-ba>"
	echo "usage: ${0} --print-header"
	exit 1
fi

if [ \( $1 = "--print-header" \) ] ; then
	echo -n "name;"
	echo -n "empty;"
	echo -n "deterministic;"
	echo -n "inherently weak;"
	echo -n "semi deterministic;"
	echo -n "terminal;"
	echo -n "unambiguous;"
	echo -n "weak;"
	echo -n "very weak;"
	echo
	exit 0
fi

INPUT=$1
WANTS_CSV=0

if [ \( "$#" -eq 2 \) -a \( "$1" = "--csv" \) ] ; then
	WANTS_CSV=1
	INPUT=$2
fi

run_autfilt () {
	local flags=$1

	cat ${INPUT} | ${AUTFILT} ${flags} > /dev/null
	if [ \( $? == 1 \) ] ; then
		echo 0
	else
		echo 1
	fi
}

is_empty=$(run_autfilt "--is-empty")
is_deterministic=$(run_autfilt "--is-deterministic")
is_inherently_weak=$(run_autfilt "--is-inherently-weak")
is_semi_deterministic=$(run_autfilt "--is-semi-deterministic")
is_terminal=$(run_autfilt "--is-terminal")
is_unambiguous=$(run_autfilt "--is-unambiguous")
is_weak=$(run_autfilt "--is-weak")
is_very_weak=$(run_autfilt "--is-very-weak")

if [ ${WANTS_CSV} == 1 ] ; then
	echo -n "${INPUT};"
	echo -n "${is_empty};"
	echo -n "${is_deterministic};"
	echo -n "${is_inherently_weak};"
	echo -n "${is_semi_deterministic};"
	echo -n "${is_terminal};"
	echo -n "${is_unambiguous};"
	echo -n "${is_weak};"
	echo -n "${is_very_weak};"
	echo
else
	echo "name: ${INPUT}"
	echo "empty: ${is_empty}"
	echo "deterministic: ${is_deterministic}"
	echo "inherently weak: ${is_inherently_weak}"
	echo "semi deterministic: ${is_semi_deterministic}"
	echo "terminal: ${is_terminal}"
	echo "unambiguous: ${is_unambiguous}"
	echo "weak: ${is_weak}"
	echo "very weak: ${is_very_weak}"
fi
