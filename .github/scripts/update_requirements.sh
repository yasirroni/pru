#!/bin/bash

set -e

PYTHON_VERSIONS=("3.7" "3.8" "3.9" "3.10" "3.11" "3.12")
UPDATED_FILES=()
DATE=$(date -u +'%Y-%m-%d')

for version in "${PYTHON_VERSIONS[@]}"; do
  echo "Processing Python $version"
  
  pyenv install -s $version
  pyenv virtualenv -f $version venv_$version
  pyenv activate venv_$version
  
  pip install pru
  
  checksum_before_single=$(md5sum pytests/requirements/${version}/requirements_single.txt | cut -d ' ' -f 1)
  checksum_before_mix=$(md5sum pytests/requirements/${version}/requirements_mix.txt | cut -d ' ' -f 1)
  
  pru -r pytests/requirements/${version}/requirements_single.txt
  pru -r pytests/requirements/${version}/requirements_mix.txt
  
  checksum_after_single=$(md5sum pytests/requirements/${version}/requirements_single.txt | cut -d ' ' -f 1)
  checksum_after_mix=$(md5sum pytests/requirements/${version}/requirements_mix.txt | cut -d ' ' -f 1)
  
  if [ "$checksum_before_single" != "$checksum_after_single" ]; then
    UPDATED_FILES+=("pytests/requirements/${version}/requirements_single.txt")
  fi
  if [ "$checksum_before_mix" != "$checksum_after_mix" ]; then
    UPDATED_FILES+=("pytests/requirements/${version}/requirements_mix.txt")
  fi
  
  pyenv deactivate
  pyenv uninstall -f venv_$version
done

if [ ${#UPDATED_FILES[@]} -ne 0 ]; then
  echo "Requirements updated. Creating pull request."
  git config --global user.email "github-actions[bot]@users.noreply.github.com"
  git config --global user.name "github-actions[bot]"
  
  BRANCH_NAME="update-requirements-${GITHUB_RUN_ID}"
  git checkout -b $BRANCH_NAME
  
  git add ${UPDATED_FILES[@]}
  git commit -m "Update requirements based on failed tests
  - Updated files: ${UPDATED_FILES[@]}
  - Date: $DATE"
  
  git push origin $BRANCH_NAME
  
  gh pr create --title "Update requirements for Python versions on $DATE" \
               --body "This PR updates the following requirements files based on the output of failed tests:\n- ${UPDATED_FILES[@]}\nDate of update: $DATE" \
               --label "update, automated-pr"
else
  echo "No requirements updated."
fi