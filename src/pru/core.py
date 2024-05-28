import re
import sys
from subprocess import PIPE, STDOUT, Popen

if sys.version_info >= (3, 8):
    IS_PYTHON_7 = False
    from importlib.metadata import PackageNotFoundError, distributions, version
else:
    IS_PYTHON_7 = True
    import pkg_resources


def read_requirements(requirements_path=None):
    if requirements_path is None:
        requirements_path = get_requirements_path()
    with open(requirements_path, "r") as f:
        requirements = f.readlines()

    # TODO: this part should be able to be simplified
    if "\x00" in requirements[0]:
        with open(requirements_path, "r", encoding="utf-16") as f:
            requirements = f.readlines()
    return requirements


def get_installed_packages_name():
    # TODO:
    #   [BUG] in Python3.7, get_installed_packages_name() did not fetch newly installed
    # packages installed from verbose_subprocess, but will be able to fetch it in the
    # second run. This is not `pkg_resources` specific, but 3.7 specific.

    if IS_PYTHON_7:
        installed_packages = [package.key for package in pkg_resources.working_set]
    else:
        installed_packages = [
            distribution.metadata["Name"] for distribution in distributions()
        ]
    return installed_packages


def get_package_version(package_name):
    if IS_PYTHON_7:
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            return None
    else:
        try:
            return version(package_name)
        except PackageNotFoundError:
            return None


def get_installed_packages_name_and_version():
    packages = {}
    for package_name in get_installed_packages_name():
        packages[package_name] = get_package_version(package_name)
    return packages


def get_requirements_packages_name(requirements_path=None):
    requirements = read_requirements(requirements_path)

    package_names = []
    for requirement in requirements:
        match = re.search(r"^([\w.-]+)", requirement, re.IGNORECASE)
        if match:
            package_names.append(match.group(1))
    return package_names


def get_installed_requirements_packages_and_version(requirements_path=None):
    packages = {}
    for package_name in get_requirements_packages_name(requirements_path):
        packages[package_name] = get_package_version(package_name)
    return packages


def replace_requirements_packages_versions(requirements_path=None, output_path=None):
    requirements = read_requirements(requirements_path)

    installed_packages_name = get_installed_packages_name()

    updated_requirements = []
    for requirement in requirements:
        # TODO:
        #   support respect all symbols
        #   support single package in multi package requirements
        match = re.search(r"^([\w.-]+)([>=<]+)?([\w.-]+)?(.*)$", requirement, re.DOTALL)
        if match:
            package_name = match.group(1)
            if package_name in installed_packages_name:
                # package installed and updated
                updated_requirements.append(
                    f"{package_name}=={get_package_version(package_name)}{match.group(4)}"
                )
            else:
                updated_requirements.append(requirement)
        else:
            # not a package, comments or whitespaces
            updated_requirements.append(requirement)

    if output_path is None:
        if requirements_path is None:
            requirements_path = get_requirements_path()
        output_path = requirements_path

    with open(output_path, "w") as f:
        f.writelines(updated_requirements)


def verbose_subprocess(command):
    with Popen(
        command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=0, close_fds=True
    ) as process:
        for line in iter(process.stdout.readline, b""):
            print(line.rstrip().decode("utf-8"))


def upgrade_installed(requirements_path=None, command="pip install --upgrade --user"):
    verbose_subprocess(
        f"{command} {' '.join(get_requirements_packages_name(requirements_path))}"
    )


def upgrade_requirements(
    requirements_path=None, output_path=None, command="pip install --upgrade --user"
):
    package_names = get_requirements_packages_name(requirements_path)
    verbose_subprocess(f"{command} {' '.join(package_names)}")
    replace_requirements_packages_versions(requirements_path, output_path)


def get_requirements_path():
    # TODO: support finding requirements file
    requirements_path = "requirements.txt"
    return requirements_path
