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
    parser.add_argument("file_path", type=str, help="Path to the requirements file.")
    parser.add_argument(
        "command",
        type=str,
        help="Command to run: print_installed, replace_versions, or upgrade_packages.",
    )
    parser.add_argument(
        "--cmd",
        type=str,
        default="pip install --upgrade",
        help="Command to use for upgrading packages.",
    )

    args = parser.parse_args()

    file_path = args.file_path
    command = args.command
    upgrade_command = args.cmd

    if command == "print_installed":
        print(get_installed_requirements_packages_and_version(file_path))
        print(get_installed_packages_name_and_version())
    elif command == "replace_versions":
        replace_requirements_packages_versions(file_path)
        print(f"Replaced versions in {file_path}")
    elif command == "upgrade_packages":
        upgrade_requirements(file_path, command=upgrade_command)
        print(f"Upgraded packages in {file_path}")
    else:
        print(
            "Unknown command. Use print_installed, replace_versions, or "
            "upgrade_packages."
        )


if __name__ == "__main__":
    main()
