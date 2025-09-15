#!/bin/bash

# Generate input pairs "<aut1>.hoa;<aut2>.hoa" by matching files that differ
# only by the suffix A.hoa vs B.hoa (and A.ba.hoa vs B.ba.hoa).
#
# Usage:
#   ./create_pairs_input.sh <folder_with_hoa_files> [output_file]
#
# Notes:
# - Traverses the folder recursively.
# - Only emits a pair when both A and B files exist.
# - Keeps the paths as returned by find (relative if input dir is relative).

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <folder_with_hoa_files> [output_file]" >&2
    exit 1
fi

HOA_FOLDER="$1"
OUTPUT_FILE="${2:-}"

if [ ! -d "$HOA_FOLDER" ]; then
    echo "Error: Directory '$HOA_FOLDER' does not exist" >&2
    exit 1
fi

# Generate pairs by scanning only *A*.hoa candidates to avoid duplicates
generate_pairs() {
    # Use plain newline-delimited listing for portability on macOS (BSD sort)
    find "$HOA_FOLDER" -type f -name "*A*.hoa" -print | LC_ALL=C sort |
    while IFS= read -r f; do
        b=""
        if [[ "$f" == *A.ba.hoa ]]; then
            b="${f%A.ba.hoa}B.ba.hoa"
        elif [[ "$f" == *A.hoa ]]; then
            b="${f%A.hoa}B.hoa"
        else
            continue
        fi

        if [ -f "$b" ]; then
            printf "%s;%s\n" "$f" "$b"
            printf "%s;%s\n" "$b" "$f"
        fi
    done
}

if [ -n "$OUTPUT_FILE" ]; then
    generate_pairs > "$OUTPUT_FILE"
    echo "Created pairs list: $OUTPUT_FILE"
else
    generate_pairs
fi
