import argparse

from pru.core import (
    get_installed_packages_name_and_version,
    get_installed_requirements_packages_and_version,
    replace_requirements_packages_versions,
    upgrade_requirements,
)


def main():
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
        "-o",
        "--output",
        type=str,
        help=(
            "Output updated packages to this file. Defaults to overwriting the input "
            "requirements file."
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
        help="Command to use for upgrading packages.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pru 0.1.0",
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
        replace_requirements_packages_versions(file_path)
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
