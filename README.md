# Python Requirements Updater

Not a [`pur`](https://github.com/alanhamlett/pip-update-requirements), but [`pru`](https://github.com/yasirroni/pru). Update and resolve `requirements.txt` based on the Python environment and pip used.

## Installation

```shell
pip install pru
```

## Usage

Using CLI:

```shell
pru "requirements.txt" upgrade_packages --cmd "pip install --upgrade"
```

Using python:

```python
file_path = 'requirements.txt'
# print(get_installed_requirements_packages_and_version(file_path))
# print(get_installed_packages_name_and_version())
# replace_requirements_packages_versions(file_path)
upgrade_requirements(file_path, command='pip install --upgrade')
```
