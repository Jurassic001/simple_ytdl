import argparse
import os
import shutil
import subprocess
import sys

WORKING_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)))


def build(clean: bool, simple: bool) -> None:
    """Builds the project using pyinstaller"""
    if clean:
        shutil.rmtree(os.path.join(WORKING_DIR, "pyinstaller"), ignore_errors=True)

    usr_platform = sys.platform
    usr_platform = "macos" if usr_platform == "darwin" else usr_platform

    executable_name = "simple_ytdl_" + usr_platform

    if not simple:
        executable_name = f"{executable_name}.{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True, cwd=WORKING_DIR).strip()}"

    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--distpath",
            "./pyinstaller/dist",
            "--workpath",
            "./pyinstaller/build",
            "--specpath",
            "./pyinstaller",
            "--name",
            executable_name,
            "--icon",
            os.path.join(WORKING_DIR, "assets/executable icon.ico"),
            "main.py",
        ],
        cwd=WORKING_DIR,
    )
    # If you change the icon file, you might have to restart file explorer for the icon to update


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clean",
        "-c",
        action="store_true",
        default=False,
        help="Remove the previous build files",
    )
    parser.add_argument(
        "--simple",
        "-s",
        action="store_true",
        default=False,
        help="Build the executable with a simple name, instead of the git hash",
    )

    args = parser.parse_args()
    build(args.clean, args.simple)
