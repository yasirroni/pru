# Python Requirements Updater

[![PyPI version](https://badge.fury.io/py/pru.svg)](https://pypi.org/project/pru/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/yasirroni/pru/blob/main/LICENSE)

Not [`pur`](https://github.com/alanhamlett/pip-update-requirements), but [`pru`](https://github.com/yasirroni/pru). It updates and resolves `requirements.txt` based on the current Python environment and `pip` version. Unlike [`Poetry`](https://python-poetry.org/docs/) and other dependency management tools, `pru` can be used outside your project and doesn't need to be included as a project dependency. Just run `pru` whenever you want to install the latest packages and update `requirements.txt` accordingly.

For example, turn this `requirements.txt`:

```txt
requests>=2.32.1
numpy<=1.26.3
pandas==2.2.1
scipy
```

into this:

```txt
requests==2.32.3
numpy==2.0.0
pandas==2.2.2
scipy==1.14.0
```

The primary purpose of `pru` is to update packages and pin their versions in `requirements.txt`. The motivation behind this is that, unlike `pyproject.toml`, `requirements.txt` should lock the versions of the packages currently used in the environment to ensure future reproducibility. This is best suited for repositories containing experiments and examples, not for package development. An article explaining `pru` also available at [Medium](https://medium.com/python-in-plain-english/simplifying-reproducibility-in-research-and-exploration-with-pru-e32fffbd7f01).


## Installation

```sh
pip install pru
```

## Usage

`pru` has multiple use cases. The main utilities (but not limited to) are:

1. `upgrade_requirements`: upgrade and pin requirements.
2. `replace_requirements_packages_versions`: update and pin the requirements file based on the installed packages.
3. `get_installed_packages_name_and_version`: list the installed packages and their versions.
4. `get_installed_requirements_packages_and_version`: list the installed packages and their versions, based on the list of packages in the requirements file.

`pru` can be used both as a Python package and from the CLI.

Using CLI:

```sh
pru
```

Explicit run using CLI:

```sh
pru -r "requirements.txt" upgrade_requirements --cmd "pip install --upgrade" -o "requirements.txt"
```

Using Python:

```python
from pru import upgrade_requirements

file_path = 'requirements.txt'
upgrade_requirements(file_path, command='pip install --upgrade')
```

Very useful in workflows:

```yaml
      - name: Upgrade pip and install dependencies
        run: |
          python -m pip install --upgrade pip
          pru
```

or to debug installed packages in a workflow:

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

In Python 3.7, `pru` *sometimes* cannot install and update requirements using a single call to `upgrade_requirements`. To fix this, simply run the command twice.
