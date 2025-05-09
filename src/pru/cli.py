"""CLI entry point for the pru package.

This module provides a command-line interface (CLI) to interact with the
`pru` package for managing and upgrading Python requirements files.

Supported commands:
- print_installed: Display currently installed packages and their versions.
- replace_versions: Overwrite versions in `requirements.txt` with installed
  versions.
- upgrade_requirements: Upgrade packages and write pinned versions to
  `requirements.txt`.

Example:
    $ pru -r requirements.txt upgrade_requirements --cmd "pip install --upgrade"
"""

import argparse

from pru.core import (
    get_installed_packages_name_and_version,
    get_installed_requirements_packages_and_version,
    replace_requirements_packages_versions,
    upgrade_requirements,
)
from pru.version import __version__


def main():
    """
    Entry point for the pru CLI.

    This function parses command-line arguments and dispatches one of the
    following actions:
    - `print_installed`: Display installed versions for packages in the
      requirements file.
    - `replace_versions`: Pin installed versions into the requirements file.
    - `upgrade_requirements`: Upgrade packages and update the file with pinned
      versions.

    Uses argparse to configure and read CLI arguments.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Notes
    -----
    - Uses `argparse` to configure CLI behavior.
    - The `--requirement` argument sets the path to the requirements file.
    - The `--output` argument sets the path to write the requirements file.
    - The `--cmd` argument customizes the shell command for pip upgrading.
    - The default command is `upgrade_requirements`.
    """

    parser = argparse.ArgumentParser(
        description="Simple Python CLI for package management."
    )
    parser.add_argument(
        "-r",
        "--requirement",
        type=str,
        default=None,
        help=(
            "Path to the requirements file. Defaults to using requirements.txt from "
            "the current directory if it exists. Use '.' to indicate no requirements "
            "file."
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="upgrade_requirements",
        help=(
            "Command to run: print_installed, replace_versions, or "
            "upgrade_requirements."
        ),
    )
    parser.add_argument(
        "--cmd",
        type=str,
        default="pip install --upgrade",
        help="Command to use for upgrading packages on upgrade_requirements.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help=(
            "Output updated packages to this file on upgrade_requirements. Defaults to "
            "overwriting the input requirements file."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"pru {__version__}",
        help="Show the version and exit.",
    )

    args = parser.parse_args()

    file_path = args.requirement
    output_path = args.output if args.output else file_path
    command = args.command
    upgrade_command = args.cmd

    if command == "print_installed":
        print(get_installed_requirements_packages_and_version(file_path))
        print(get_installed_packages_name_and_version())
    elif command == "replace_versions":
        replace_requirements_packages_versions(file_path, output_path)
        print(f"Replaced versions in {file_path}")
    elif command == "upgrade_requirements":
        upgrade_requirements(
            file_path, output_path=output_path, command=upgrade_command
        )
        print(f"Upgraded packages in {file_path}")
    else:
        print(
            "Unknown command. Use print_installed, replace_versions, or "
            "upgrade_requirements."
        )


if __name__ == "__main__":
    main()
