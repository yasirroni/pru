# Contributing

## Environment

```shell
python3.12 -m venv env3_12
source env3_12/bin/activate
```

```shell
python3.7 -m venv env3_7
source env3_7/bin/activate
```

## Install requirements

```shell
pip install -r requirements.txt
```

## Install package in development mode

```shell
pip install ."[dev]"
```

## Pre-Commit

```shell
pre-commit install
pre-commit run --all-files
```

## Test

```shell
python3 -m pytest . -rA -c pyproject.toml --cov-report term-missing --cov=src/pru
```

## Clean installed packages from test

```shell
pip uninstall -y requests numpy pandas scipy
pip cache purge
```
