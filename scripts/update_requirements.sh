#!/bin/bash

set -e

PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12" "3.13" "3.14")
UPDATED_FILES=()
DATE=$(date -u +'%Y-%m-%d')

# Function to get md5 hash (cross-platform)
get_md5() {
  if command -v md5sum &> /dev/null; then
    md5sum "$1" | cut -d ' ' -f 1
  elif command -v md5 &> /dev/null; then
    md5 -q "$1"
  else
    echo "Error: No MD5 tool found" >&2
    exit 1
  fi
}

for version in "${PYTHON_VERSIONS[@]}"; do
  echo "=== Processing Python $version ==="
  
  source "env${version}/bin/activate"

  # Install pru into the virtual environment
  pip install ."[dev]"

  # Get minor version
  minor_version=$(python -c "import sys; print(f'{sys.version_info.minor}')")

  # Calculate checksums before running pru
  checksum_before_single=$(get_md5 "pytests/requirements/3_${minor_version}/requirements_single_updated.txt")
  checksum_before_mix=$(get_md5 "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt")

  # Run pru to update requirements within the virtual environment
  pru -r "pytests/requirements/3_${minor_version}/requirements_single_updated.txt"
  pru -r "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt"

  # Calculate checksums after running pru
  checksum_after_single=$(get_md5 "pytests/requirements/3_${minor_version}/requirements_single_updated.txt")
  checksum_after_mix=$(get_md5 "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt")

  # Check if any requirements file was updated
  if [ "$checksum_before_single" != "$checksum_after_single" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_single_updated.txt")
  fi
  if [ "$checksum_before_mix" != "$checksum_after_mix" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_mix_updated.txt")
  fi

  deactivate
done

if [ ${#UPDATED_FILES[@]} -ne 0 ]; then
  echo ""
  echo "Requirements updated:"
  printf '%s\n' "${UPDATED_FILES[@]}"
  echo "Update date: $DATE"
else
  echo ""
  echo "No requirements updated."
fi
