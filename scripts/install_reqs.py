# region setup
# all package imports are part of the Python standard library
import argparse
import os
import subprocess
import sys

ROOT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)))

# set up color codes
RED: str = "\033[0;31m"
GREEN: str = "\033[0;32m"
CYAN: str = "\033[0;36m"
NC: str = "\033[0m"  # No color


# set up method for formatting terminal output
def print_with_sidebars(text: str = "", color_code: str = NC) -> None:
    """Adds "sidebars" in the form of `=` to each side of a string and prints it

    Args:
        text (str, optional): The string blessed with "sidebars". Leaving this blank will print a full line of `=`
        color_code (str, optional): Escape code of a certain color to wrap the text in. Leaving this blank will not color the text
    """
    # Check to see if standard output is connected to a terminal. If yes get the terminal width, otherwise set a default value
    terminal_width = os.get_terminal_size().columns if os.isatty(sys.stdout.fileno()) else 80

    if not text:
        msg = "=" * terminal_width
    else:
        void_len = len(text) + 2  # Define the "void" area where the string will go
        sidebar_len = (terminal_width - void_len) // 2  # Define the length of a single sidebar
        sidebar = "=" * sidebar_len  # Make the sidebars
        msg = f"{sidebar} {color_code}{text}{NC} {sidebar}"
    print(msg)


# region main method
def main(strict: bool) -> None:
    # make sure pip and wheel are up-to-date
    print_with_sidebars("Pre-execution checks", CYAN)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "wheel", "pip", "--upgrade"],
        check=True,
    )

    # check if we're outside a virtual environment and container and CI
    if (
        sys.base_prefix == sys.prefix  # no virtual environment
        and not os.path.exists("/.dockerenv")  # no container
        and os.getenv("CI") is None  # no github actions
        and os.getenv("BUILD_BUILDID") is None  # no azure pipelines
    ):
        print_with_sidebars("Not inside a docker container/virtual environment, exiting", RED)
        sys.exit(1)

    # Install requirements.txt
    print_with_sidebars("Installing requirements", CYAN)
    subprocess.run(
        [
            "pip",
            "install",
            "-r",
            "requirements.txt",
        ],
        check=strict,
        cwd=ROOT_DIR,
    )

    print_with_sidebars("Setting up git hooks", CYAN)
    # Setup pre-commit hooks
    subprocess.run(
        ["pre-commit", "install"],
        check=strict,
        cwd=ROOT_DIR,
    )
    # Setup Git Large File System
    subprocess.run(
        ["git", "lfs", "install"],
        check=strict,
        cwd=ROOT_DIR,
    )
    print_with_sidebars("Requirement installation/setup successful", GREEN)
    sys.exit(0)


# region execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        default=True,
        help="Fail if ANY requirements could not installed",
    )

    args = parser.parse_args()
    main(args.strict)
