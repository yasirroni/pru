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
    """
    Read lines from a requirements file and return them as a list.

    Handles UTF-16 encoding fallback when UTF-8 fails, to support some Windows
    generated files.

    Parameters
    ----------
    requirements_path : str or None, optional
        Path to the requirements file. If None, uses `get_requirements_path()`.

    Returns
    -------
    list of str
        Lines from the requirements file.
    """

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
    """
    Get the names of all installed packages in the current environment.

    Uses importlib.metadata or pkg_resources depending on the Python version.
    In Python 3.7, repeated calls may be needed to capture newly installed
    packages after subprocess execution.

    Returns
    -------
    list of str
        Names of all installed packages.
    """

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
    """
    Get the installed version of a specific package.

    Compatible with both Python 3.7 (via pkg_resources) and 3.8+ (via
    importlib.metadata).

    Parameters
    ----------
    package_name : str
        Name of the package to look up.

    Returns
    -------
    str or None
        The installed version of the package, or None if not found.
    """

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
    """
    Get a mapping of all installed packages to their installed versions.

    Returns
    -------
    dict
        Dictionary of {normalized_package_name: version}.

    Notes
    -----
    - Uses pip's internal `pkg_resources` to gather installed packages.
    - Normalizes names using PEP 503 to ensure compatibility.
    """
    packages = {}
    for package_name in get_installed_packages_name():
        packages[package_name] = get_package_version(package_name)
    return packages


def get_requirements_packages_name(requirements_path=None):
    """
    Extract package names from a requirements file.

    Parameters
    ----------
    requirements_path : str or None, optional
        Path to the requirements file. If None, defaults to the result of
        `get_requirements_path()`.

    Returns
    -------
    list of str
        List of package names found in the requirements file. Version
        constraints are removed.
    """

    requirements = read_requirements(requirements_path)

    package_names = []
    for requirement in requirements:
        match = re.search(r"^([\w.-]+)", requirement, re.IGNORECASE)
        if match:
            package_names.append(match.group(1))
    return package_names


def get_installed_requirements_packages_and_version(requirements_path=None):
    """
    Get installed versions for packages listed in a requirements file.

    Parses a requirements.txt-style file and compares the listed package
    names with the current Python environment. Returns a dictionary
    mapping package names to the installed version. If a package is not
    installed, its value will be `None`.

    Parameters
    ----------
    requirements_path : str or None, optional
        Path to the requirements file. Defaults to "requirements.txt" in
        the current directory if None is provided.

    Returns
    -------
    dict
        Dictionary of {package_name: installed_version}.

    Notes
    -----
    - Does not resolve sub-dependencies or transitive dependencies.
    - Package names are normalized using PEP 503 normalization rules.
    """

    packages = {}
    for package_name in get_requirements_packages_name(requirements_path):
        packages[package_name] = get_package_version(package_name)
    return packages


def replace_requirements_packages_versions(requirements_path=None, output_path=None):
    """
    Replace versions in a requirements file with installed versions.

    This function scans a requirements.txt-style file and replaces each
    package entry with its current version from the Python environment.
    The version will be pinned using `==`, which helps ensure reproducible
    installations.

    Parameters
    ----------
    requirements_path : str
        Path to the input requirements file. Will be overwritten in-place.
    output_path : str
        Path to the output requirements file. Will be overwritten in-place.

    Notes
    -----
    - Package names are normalized using PEP 503 rules.
    - Uninstalled packages are left unchanged.

    See Also
    --------
    get_installed_packages_name_and_version : Used internally to obtain
        installed versions for the listed packages.
    """

    requirements = read_requirements(requirements_path)

    installed_packages = get_installed_packages_name_and_version()

    name_mapping = {}
    for pkg_name in installed_packages:
        # create normalized key from what is installed
        normalized = pkg_name.lower().replace("-", "_")

        # store original name
        name_mapping[normalized] = pkg_name

    updated_requirements = []
    for requirement in requirements:
        # TODO:
        #   support respect all symbols
        #   support single package in multi package requirements
        #   support verboste to print what is is updated
        match = re.search(r"^([\w.-]+)([>=<]+)?([\w.-]+)?(.*)$", requirement, re.DOTALL)
        if match:
            req_pkg_name = match.group(1)

            # normalized what is in requirements.txt
            normalized_req = req_pkg_name.lower().replace("-", "_")

            if normalized_req in name_mapping:
                installed_pkg_name = name_mapping[normalized_req]
                # package installed and updated
                updated_requirements.append(
                    f"{req_pkg_name}=="
                    f"{installed_packages[installed_pkg_name]}{match.group(4)}"
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
    """
    Run a subprocess command and print real-time output to the console.

    Useful for observing pip upgrade/install output as it happens. Lines are
    printed to stdout as soon as they are received.

    Parameters
    ----------
    command : str
        The shell command to execute.

    Returns
    -------
    None
    """

    with Popen(
        command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=0, close_fds=True
    ) as process:
        for line in iter(process.stdout.readline, b""):
            print(line.rstrip().decode("utf-8"))


def upgrade_installed(requirements_path=None, command="pip install --upgrade --user"):
    """
    Upgrade all installed packages listed in the requirements file.

    This function does not write back any updated version numbers to the
    file. It simply performs the upgrade using the provided shell command.

    Parameters
    ----------
    requirements_path : str
        Path to the requirements file to read package names from.
    command : str
        Command used to upgrade each package, e.g.
        "pip install --upgrade --user".

    Notes
    -----
    - Useful when you want to upgrade but not pin the versions.
    - Used internally by `upgrade_requirements`.
    """

    verbose_subprocess(
        f"{command} {' '.join(get_requirements_packages_name(requirements_path))}"
    )


def upgrade_requirements(
    requirements_path=None, output_path=None, command="pip install --upgrade --user"
):
    """
    Upgrade all packages listed in requirements.txt and pin their versions.

    This function performs two major tasks to help maintain a reproducible
    Python environment:
    1. It upgrades all packages listed in a requirements file by calling pip
       with the provided command.
    2. It rewrites the requirements file (or writes to an output path) by
       pinning the version of each package to the exact version installed
       after the upgrade.

    This resolves dependency hell by aligning declared versions with the
    actual environment state, reducing the risk of version mismatch or
    unintentional upgrades during deployment.

    Parameters
    ----------
    requirements_path : str or None, optional
        Path to the input requirements file. If None, defaults to
        "requirements.txt" in the current directory.
    output_path : str or None, optional
        Path to the output file to write the updated, pinned requirements.
        If None, will overwrite the input file.
    command : str, optional
        Shell command used to perform the upgrade. Default is
        "pip install --upgrade --user". The command is appended with
        package names before execution.

    Notes
    -----
    - The function internally uses subprocess to call pip via
      `verbose_subprocess`.
    - The version pinning is done using `==` for each package, matching the
      version found in the current environment.
    - The function normalizes package names to resolve discrepancies like
      `some-pkg` vs `some_pkg`.

    See Also
    --------
    replace_requirements_packages_versions : Pin installed versions to
        requirements file without upgrading.
    upgrade_installed : Upgrade packages without rewriting the requirements
        file.
    """

    package_names = get_requirements_packages_name(requirements_path)
    verbose_subprocess(f"{command} {' '.join(package_names)}")
    replace_requirements_packages_versions(requirements_path, output_path)


def get_requirements_path():
    """
    Determine the default path to the requirements file.

    Currently returns "requirements.txt" unconditionally. Placeholder for
    future enhancements to search for common requirements filenames.

    Returns
    -------
    str
        Path to the default requirements file.
    """

    # TODO: support finding requirements file
    requirements_path = "requirements.txt"
    return requirements_path
