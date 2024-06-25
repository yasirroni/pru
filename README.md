# Python Requirements Updater

Not a [`pur`](https://github.com/alanhamlett/pip-update-requirements), but [`pru`](https://github.com/yasirroni/pru). Update and resolve `requirements.txt` based on the Python environment and pip used. Unlike [`Poetry`](https://python-poetry.org/docs/) and other dependencies management packages, you can use `pru` outside your project and exclude it from your project dependency. Just run `pru` whenever you feel like installing the latest package and update `requirements.txt` accordingly.

## Installation

```shell
pip install pru
```

## Usage

Using CLI:

```shell
pru
```

Explicit run using CLI:

```shell
pru "requirements.txt" upgrade_requirements --cmd "pip install --upgrade"
```

Using python:

```python
from pru import (
    get_installed_requirements_packages_and_version,
    get_installed_packages_name_and_version,
    replace_requirements_packages_versions,
    upgrade_requirements,
)


file_path = 'requirements.txt'
# print(get_installed_requirements_packages_and_version(file_path))
# print(get_installed_packages_name_and_version())
# replace_requirements_packages_versions(file_path)
upgrade_requirements(file_path, command='pip install --upgrade')
```

Very useful on workflow:

```yaml
      - name: Upgrade pip and install dependencies
        run: |
          python -m pip install --upgrade pip
          pru
```

Or to debug installed package on workflow:

```yaml
      - name: Run pru if tests fail
        if: steps.pytest.outcome != 'success'
        run: |
          python_version_minor=$(python -c "import sys; print(f'{sys.version_info.minor}')")
          pru -r pytests/requirements/3_${python_version_minor}/requirements.txt
          echo "Contents of pytests/requirements/3_${python_version_minor}/requirements.txt:"
          cat pytests/requirements/3_${python_version_minor}/requirements.txt
```

## Known Issue

In python3.7, `pru` "sometimes" can't install and update requirements using a single call
of `upgrade_requirements`. To fix this, simply run two times.
