#!/bin/bash
# Similar to create_incl_input.sh but for inclusion benchmarks over .aut /.autfilt files.
# Pairs files with the same basename where one ends with 'sup.aut' and the other 'sub.aut'
# and likewise for 'sup.autfilt' / 'sub.autfilt'.
#
# Output format (one pair per line):
#   <sup_file>;<sub_file>
# By default emits only the logical direction sup;sub. If --both is passed as the
# last argument, it will also emit the reverse order.
#
# Usage:
#   ./create_incl_aut_input.sh <folder_with_aut_files> [output_file] [--both]
# Notes:
#   - Traverses the folder recursively.
#   - Only emits a pair when both sup and sub variants exist.
#   - Keeps paths as returned by find (relative if input dir is relative).
#   - Designed to be POSIX-ish; relies on bash pattern substitution.
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <folder_with_aut_files> [output_file] [--both]" >&2
  exit 1
fi

AUT_FOLDER="$1"
OUTPUT_FILE=""
EMIT_BOTH="1"

if [ ! -d "$AUT_FOLDER" ]; then
  echo "Error: Directory '$AUT_FOLDER' does not exist" >&2
  exit 1
fi

# Parse optional args
if [ "$#" -ge 2 ]; then
  if [ "${2:-}" != "--both" ]; then
    OUTPUT_FILE="$2"
  else
    EMIT_BOTH="1"
  fi
fi
if [ "$#" -ge 3 ]; then
  if [ "${3:-}" = "--both" ]; then
    EMIT_BOTH="1"
  else
    echo "Unknown third argument: $3" >&2
    exit 1
  fi
fi

emit_pairs() {
  # Limit initial scan to *sup.aut* to avoid duplicates; handle .aut and .autfilt separately.
  find "$AUT_FOLDER" -type f \( -name "*sup.autfilt" \) -print | LC_ALL=C sort |
  while IFS= read -r f; do
    partner=""
    if [[ "$f" == *sup.autfilt ]]; then
      partner="${f%sup.autfilt}sub.autfilt"
    elif [[ "$f" == *sup.aut ]]; then
      partner="${f%sup.aut}sub.aut"
    else
      continue
    fi
    if [ -f "$partner" ]; then
      printf "%s;%s\n" "$f" "$partner"
      if [ "$EMIT_BOTH" = "1" ]; then
        printf "%s;%s\n" "$partner" "$f"
      fi
    fi
  done
}

if [ -n "$OUTPUT_FILE" ]; then
  emit_pairs > "$OUTPUT_FILE"
  echo "Created inclusion pairs list: $OUTPUT_FILE" >&2
else
  emit_pairs
fi
