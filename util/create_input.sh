#!/bin/bash

# Script to create a list of .hoa files with relative paths
# Usage: ./create_hoa_list.sh <folder_with_hoa_files> [output_file]

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <folder_with_hoa_files> [output_file]"
    echo "  folder_with_hoa_files: Directory containing .hoa files (searched recursively)"
    echo "  output_file: Optional output file (default: writes to stdout)"
    exit 1
fi

HOA_FOLDER="$1"
OUTPUT_FILE="$2"

# Check if the folder exists
if [ ! -d "$HOA_FOLDER" ]; then
    echo "Error: Directory '$HOA_FOLDER' does not exist"
    exit 1
fi

# Function to create the list
create_hoa_list() {
    find "$HOA_FOLDER" -name "*.hoa" -type f | sort
}

# Output to file or stdout
if [ -n "$OUTPUT_FILE" ]; then
    create_hoa_list > "$OUTPUT_FILE"
    echo "Created list of .hoa files in: $OUTPUT_FILE"
else
    create_hoa_list
fi
