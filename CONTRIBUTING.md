# Contributing

## Environment

```sh
python3.7 -m venv env3_7
source env3_7/bin/activate
```

```sh
uv venv env3.14 --python 3.14
source env3.14/bin/activate
uv pip install pip
```

## Install requirements

```sh
pip install -r requirements.txt
```

## Install package in development mode

```sh
pip install ."[dev]"
```

## Pre-Commit

```sh
pre-commit install
pre-commit run --all-files
```

## Test

```sh
python3 -m pytest . -rA -c pyproject.toml --cov-report term-missing --cov=src/pru
```

## Clean installed packages from test

```sh
pip uninstall -y requests numpy pandas scipy
pip cache purge
```

## Run all

```sh
for version in 3.8 3.9 3.10 3.11 3.12 3.13 3.14; do
  uv venv env$version --python $version
  source env$version/bin/activate
  uv pip install pip
  deactivate
done
```

```sh
chmod +x scripts/update_requirements.sh
./scripts/update_requirements.sh
```

```sh
for version in 3.8 3.9 3.10 3.11 3.12 3.13 3.14; do
  echo "=== Testing Python $version ==="
  source env$version/bin/activate
  pip install ."[dev]"
  python3 -m pytest . -rA -c pyproject.toml --cov-report term-missing --cov=src/pru
  deactivate
done
```
