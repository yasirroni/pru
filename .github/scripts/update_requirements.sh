#!/bin/bash

set -e

PYTHON_VERSIONS=("3.7" "3.8" "3.9" "3.10" "3.11" "3.12")
UPDATED_FILES=()
DATE=$(date -u +'%Y-%m-%d')

for version in "${PYTHON_VERSIONS[@]}"; do
  echo "Processing Python $version"
  
  # Create virtual environment
  python3 -m venv env_$version
  source env_$version/bin/activate
  
  # Ensure pip is up-to-date
  pip install --upgrade pip
  
  # Install pru
  pip install pru

  minor_version=$(python -c "import sys; print(f'{sys.version_info.minor}')")
  
  # Calculate checksums before running pru
  checksum_before_single=$(md5sum pytests/requirements/3_${minor_version}/requirements_single_updated.txt | cut -d ' ' -f 1)
  checksum_before_mix=$(md5sum pytests/requirements/3_${minor_version}/requirements_mix_updated.txt | cut -d ' ' -f 1)
  
  # Run pru to update requirements
  pru -r pytests/requirements/3_${minor_version}/requirements_single_updated.txt
  pru -r pytests/requirements/3_${minor_version}/requirements_mix_updated.txt
  
  # Calculate checksums after running pru
  checksum_after_single=$(md5sum pytests/requirements/3_${minor_version}/requirements_single_updated.txt | cut -d ' ' -f 1)
  checksum_after_mix=$(md5sum pytests/requirements/3_${minor_version}/requirements_mix_updated.txt | cut -d ' ' -f 1)
  
  # Check if any requirements file was updated
  if [ "$checksum_before_single" != "$checksum_after_single" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_single_updated.txt")
  fi
  if [ "$checksum_before_mix" != "$checksum_after_mix" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_mix_updated.txt")
  fi
  
  # Deactivate and remove the virtual environment
  deactivate
  rm -rf env_$version
done

if [ ${#UPDATED_FILES[@]} -ne 0 ]; then
  echo "Requirements updated. Creating pull request."
  echo "::set-output name=updated::true"
  echo "::set-output name=updated_files::${UPDATED_FILES[*]}"
  echo "::set-output name=update_date::$DATE"
else
  echo "No requirements updated."
  echo "::set-output name=updated::false"
fi
