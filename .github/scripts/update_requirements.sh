#!/bin/bash

set -e

PYTHON_VERSIONS=("3.7" "3.8" "3.9" "3.10" "3.11" "3.12")
UPDATED_FILES=()
DATE=$(date -u +'%Y-%m-%d')

# Function to install Python if not already installed
install_python() {
  local version="$1"
  
  if ! command -v python${version} &> /dev/null; then
    echo "Python ${version} not found. Installing..."
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python${version} python${version}-venv
  else
    echo "Python ${version} is already installed."
  fi
}

for version in "${PYTHON_VERSIONS[@]}"; do
  echo "Processing Python $version"
  
  # Install Python if not already installed
  install_python "$version"
  
  # Create virtual environment specific to the current Python version
  python${version} -m venv "env_${version}"
  source "env_${version}/bin/activate"
  
  # Install pip using get-pip.py if it's not already installed
  if ! command -v pip &> /dev/null; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
  fi
  
  # Ensure pip is up-to-date within the virtual environment
  pip install --upgrade pip
  
  # Install pru into the virtual environment
  pip install pru
  
  # Get minor version
  minor_version=$(python${version} -c "import sys; print(f'{sys.version_info.minor}')")

  # Calculate checksums before running pru
  checksum_before_single=$(md5sum "pytests/requirements/3_${minor_version}/requirements_single_updated.txt" | cut -d ' ' -f 1)
  checksum_before_mix=$(md5sum "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt" | cut -d ' ' -f 1)
  
  # Run pru to update requirements within the virtual environment
  pru -r "pytests/requirements/3_${minor_version}/requirements_single_updated.txt"
  pru -r "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt"
  
  # Calculate checksums after running pru
  checksum_after_single=$(md5sum "pytests/requirements/3_${minor_version}/requirements_single_updated.txt" | cut -d ' ' -f 1)
  checksum_after_mix=$(md5sum "pytests/requirements/3_${minor_version}/requirements_mix_updated.txt" | cut -d ' ' -f 1)
  
  # Check if any requirements file was updated
  if [ "$checksum_before_single" != "$checksum_after_single" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_single_updated.txt")
  fi
  if [ "$checksum_before_mix" != "$checksum_after_mix" ]; then
    UPDATED_FILES+=("pytests/requirements/3_${minor_version}/requirements_mix_updated.txt")
  fi
  
  # Deactivate the virtual environment
  deactivate
  # Remove the virtual environment directory
  rm -rf "env_${version}"
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
