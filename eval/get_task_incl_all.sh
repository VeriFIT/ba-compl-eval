#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$#" -ne 1 ]; then
    echo "ERROR: script expects exactly one argument - path to a file with task names (one per line)"
    exit -1
fi

input_file="$1"

if [ ! -f "$input_file" ]; then
    echo "ERROR: input file '$input_file' not found"
    exit -1
fi

# Read all lines using cat and process each line
for line in $(cat "$input_file"); do
    # Skip empty lines
    [[ -z "$line" ]] && continue
    echo "$line"
    echo "Processing task: $line"
    "$SCRIPT_DIR/get_task_incl.sh" "$line"
done
