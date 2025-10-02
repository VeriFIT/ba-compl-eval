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

# Default mode: look for .aut/.autfilt files. If --ba is supplied, look for .ba files
BA_MODE=0

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--ba] <folder_with_aut_files> [output_file] [--both]" >&2
  exit 1
fi

# Optional first arg --ba
if [ "$1" = "--ba" ]; then
  BA_MODE=1
  shift
fi

AUT_FOLDER="$1"
OUTPUT_FILE=""
EMIT_BOTH="1"

if [ ! -d "$AUT_FOLDER" ]; then
  echo "Error: Directory '$AUT_FOLDER' does not exist" >&2
  exit 1
fi

# Parse optional args (output file and optional --both)
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

deduplicate_files() {
  # Deduplicate files by base name, preferring aligned versions
  awk '
    {
      # Extract base name by removing the suffix
      if ($0 ~ /sup\.autfilt\.aligned\.ba$/) {
        base = $0; sub(/sup\.autfilt\.aligned\.ba$/, "", base)
        suffix = "sup.autfilt.aligned.ba"
      } else if ($0 ~ /sup\.autfilt\.ba$/) {
        base = $0; sub(/sup\.autfilt\.ba$/, "", base)
        suffix = "sup.autfilt.ba"
      } else if ($0 ~ /sub\.autfilt\.aligned\.ba$/) {
        base = $0; sub(/sub\.autfilt\.aligned\.ba$/, "", base)
        suffix = "sub.autfilt.aligned.ba"
      } else if ($0 ~ /sub\.autfilt\.ba$/) {
        base = $0; sub(/sub\.autfilt\.ba$/, "", base)
        suffix = "sub.autfilt.ba"
      } else if ($0 ~ /sup\.autfilt\.aligned$/) {
        base = $0; sub(/sup\.autfilt\.aligned$/, "", base)
        suffix = "sup.autfilt.aligned"
      } else if ($0 ~ /sup\.autfilt$/) {
        base = $0; sub(/sup\.autfilt$/, "", base)
        suffix = "sup.autfilt"
      } else if ($0 ~ /sub\.autfilt\.aligned$/) {
        base = $0; sub(/sub\.autfilt\.aligned$/, "", base)
        suffix = "sub.autfilt.aligned"
      } else if ($0 ~ /sub\.autfilt$/) {
        base = $0; sub(/sub\.autfilt$/, "", base)
        suffix = "sub.autfilt"
      }
      
      # If we have not seen this base, or if current is aligned and stored is not, update
      if (!(base in seen)) {
        seen[base] = $0
        aligned[base] = (suffix ~ /aligned/)
      } else if (suffix ~ /aligned/ && !aligned[base]) {
        # Current is aligned but stored is not, prefer aligned
        seen[base] = $0
        aligned[base] = 1
      }
      # Otherwise keep the existing entry (already aligned or non-aligned is fine)
    }
    END {
      for (base in seen) {
        print seen[base]
      }
    }
  '
}

emit_pairs() {
  # Choose name pattern based on mode to find and deduplicate sup variants
  if [ "$BA_MODE" -eq 1 ]; then
    # In BA mode, consider both aligned and non-aligned sup variants
    find "$AUT_FOLDER" -type f \( -name "*sup.autfilt.ba" -o -name "*sup.autfilt.aligned.ba" \) -print
  else
    # In HOA mode, consider both aligned and non-aligned sup variants
    find "$AUT_FOLDER" -type f \( -name "*sup.autfilt" -o -name "*sup.autfilt.aligned" \) -print
  fi | LC_ALL=C sort | deduplicate_files | LC_ALL=C sort |
  while IFS= read -r f; do
    base=""
    # Extract base name
    if [ "$BA_MODE" -eq 1 ]; then
      if [[ "$f" == *sup.autfilt.aligned.ba ]]; then
        base="${f%sup.autfilt.aligned.ba}"
      elif [[ "$f" == *sup.autfilt.ba ]]; then
        base="${f%sup.autfilt.ba}"
      else
        continue
      fi
    else
      if [[ "$f" == *sup.autfilt.aligned ]]; then
        base="${f%sup.autfilt.aligned}"
      elif [[ "$f" == *sup.autfilt ]]; then
        base="${f%sup.autfilt}"
      else
        continue
      fi
    fi
    
    # Find matching sub file, preferring aligned version
    emit_partner=""
    if [ "$BA_MODE" -eq 1 ]; then
      # Check for aligned sub first, then non-aligned
      if [ -f "${base}sub.autfilt.aligned.ba" ]; then
        emit_partner="${base}sub.autfilt.aligned.ba"
      elif [ -f "${base}sub.autfilt.ba" ]; then
        emit_partner="${base}sub.autfilt.ba"
      fi
    else
      # Check for aligned sub first, then non-aligned
      if [ -f "${base}sub.autfilt.aligned" ]; then
        emit_partner="${base}sub.autfilt.aligned"
      elif [ -f "${base}sub.autfilt" ]; then
        emit_partner="${base}sub.autfilt"
      fi
    fi
    
    if [ -n "$emit_partner" ]; then
      printf "%s;%s\n" "$f" "$emit_partner"
      if [ "$EMIT_BOTH" = "1" ]; then
        printf "%s;%s\n" "$emit_partner" "$f"
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
