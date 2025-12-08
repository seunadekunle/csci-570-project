#!/bin/bash

# CSCI 570 Submission ZIP Creator
# Creates a properly structured submission zip file

echo "=== CSCI 570 Submission ZIP Creator ==="
echo ""

# Prompt for USC IDs
echo "Enter USC IDs separated by spaces (e.g., 1234567891 1234567892 1234567893):"
read -r ids_input

# Validate input
if [ -z "$ids_input" ]; then
    echo "Error: No USC IDs provided."
    exit 1
fi

# Convert space-separated IDs to underscore-separated
ids_array=($ids_input)
folder_name=$(IFS=_; echo "${ids_array[*]}")
zip_name="${folder_name}.zip"

echo ""
echo "Creating submission with:"
echo "  Folder: $folder_name"
echo "  ZIP:    $zip_name"
echo ""

# Check required files exist
required_files=("basic.py" "efficient.py" "basic.sh" "efficient.sh")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

# Check for Summary.pdf
if [ ! -f "Summary.pdf" ]; then
    echo "Warning: Summary.pdf not found. Please add it before final submission."
fi

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "Error: Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

# Clean up any existing submission folder/zip
rm -rf "$folder_name" "$zip_name" 2>/dev/null

# Create folder structure
mkdir -p "$folder_name"

# Copy required files
cp basic.py "$folder_name/"
cp efficient.py "$folder_name/"
cp basic.sh "$folder_name/"
cp efficient.sh "$folder_name/"

# Copy Summary.pdf if it exists
if [ -f "Summary.pdf" ]; then
    cp Summary.pdf "$folder_name/"
    echo "✓ Summary.pdf included"
else
    echo "⚠ Summary.pdf not included (file not found)"
fi

# Create the zip file
zip -r "$zip_name" "$folder_name"

# Clean up the temporary folder
rm -rf "$folder_name"

echo ""
echo "=== Submission ZIP created successfully ==="
echo "File: $zip_name"
echo ""
echo "Contents:"
unzip -l "$zip_name"
