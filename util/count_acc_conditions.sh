#!/bin/bash

AUTFILT="autfilt"

if [ "$#" -ne 1 ]; then
    echo "Usage: ${0} <folder>"
    exit 1
fi

FOLDER="$1"

if [ ! -d "$FOLDER" ]; then
    echo "Error: '${FOLDER}' is not a directory"
    exit 1
fi

# Find all .hoa files and gather acceptance conditions
results=$(find "$FOLDER" -maxdepth 1 -name "*.hoa" -print0 \
    | xargs -0 -I{} "$AUTFILT" --stats="%G" "{}" 2>/dev/null \
    | grep -v '^$')

if [ -z "$results" ]; then
    echo "No .hoa files found or no acceptance conditions could be extracted in '${FOLDER}'"
    exit 0
fi

echo "Acceptance condition counts:"
printf "%-10s  %s\n" "Count" "Acceptance condition"
printf "%-10s  %s\n" "-----" "--------------------"
echo "$results" | sort | uniq -c | sort -rn | while read count acc; do
    printf "%-10d  %s\n" "$count" "$acc"
done
