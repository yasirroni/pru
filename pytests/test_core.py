import os

import pytest
from pru.core import (
    get_installed_packages_name,
    get_installed_packages_name_and_version,
    get_installed_requirements_packages_and_version,
    get_package_version,
    get_requirements_packages_name,
    read_requirements,
    replace_requirements_packages_versions,
    upgrade_installed,
    upgrade_requirements,
    verbose_subprocess,
)


@pytest.fixture
def requirements_dir():
    return "pytests/requirements"


def test_read_requirements(requirements_dir):
    requirements_path = os.path.join(
        requirements_dir, "requirements_single_package.txt"
    )
    result = read_requirements(requirements_path)
    assert result == ["requests\n"]


def test_get_installed_packages_name():
    result = get_installed_packages_name()
    assert "pip" in result  # assuming pip is always installed


def test_get_package_version():
    version = get_package_version("pip")
    assert version is not None


def test_get_installed_packages_name_and_version():
    packages = get_installed_packages_name_and_version()
    assert "pip" in packages
    assert packages["pip"] is not None


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("requirements_single_package.txt", ["requests"]),
        ("requirements_mix.txt", ["requests", "numpy", "pandas", "scipy"]),
    ],
)
def test_get_requirements_packages_name(requirements_dir, file_name, expected):
    requirements_path = os.path.join(requirements_dir, file_name)
    result = get_requirements_packages_name(requirements_path)
    assert result == expected


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("requirements_single_package.txt", {"requests": None}),
        ("requirements_mix.txt", {"requests": None, "numpy": None, "pandas": None}),
    ],
)
def test_get_installed_requirements_packages_and_version(
    requirements_dir, file_name, expected
):
    requirements_path = os.path.join(requirements_dir, file_name)
    result = get_installed_requirements_packages_and_version(requirements_path)
    for package in expected:
        assert package in result


@pytest.mark.parametrize(
    "file_name, expected_file",
    [
        ("requirements_single_package.txt", "requirements_single_package_updated.txt"),
        ("requirements_mix.txt", "requirements_mix_updated.txt"),
    ],
)
def test_replace_requirements_packages_versions(
    requirements_dir, file_name, expected_file
):
    requirements_path = os.path.join(requirements_dir, file_name)
    expected_path = os.path.join(requirements_dir, expected_file)

    with open(expected_path, "r") as f:
        expected = f.readlines()

    replace_requirements_packages_versions(requirements_path)

    with open(requirements_path, "r") as f:
        result = f.readlines()

    assert result == expected


def test_verbose_subprocess():
    command = "echo test"
    verbose_subprocess(command)  # This should print "test" to stdout


def test_upgrade_installed(requirements_dir):
    requirements_path = os.path.join(
        requirements_dir, "requirements_single_package.txt"
    )
    upgrade_installed(requirements_path, command="pip install --upgrade")


@pytest.mark.parametrize(
    "file_name, expected_file",
    [
        ("requirements_single_package.txt", "requirements_single_package_updated.txt"),
        ("requirements_mix.txt", "requirements_mix_updated.txt"),
    ],
)
def test_upgrade_requirements(requirements_dir, file_name, expected_file):
    requirements_path = os.path.join(requirements_dir, file_name)
    expected_path = os.path.join(requirements_dir, expected_file)

    with open(expected_path, "r") as f:
        expected = f.readlines()

    upgrade_requirements(requirements_path, command="pip install --upgrade")

    with open(requirements_path, "r") as f:
        result = f.readlines()

    assert result == expected
