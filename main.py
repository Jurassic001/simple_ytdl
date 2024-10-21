import argparse
import os
import subprocess
import sys
import time
from typing import Literal

import keyboard as kb
import pyperclip

RED: str = "\033[0;31m"
GREEN: str = "\033[0;32m"
CYAN: str = "\033[0;36m"
NC: str = "\033[0m"  # No color


class FallbackInputTrigger(Exception):
    """Exception to trigger the fallback input method"""

    def __init__(self) -> None:
        super().__init__("Fallback input triggered due to user input")


class simple_ytdl:
    def __init__(self, yes: bool, arg_url: str) -> None:
        self.EXT_DICT: dict[bool, str] = {
            True: "mp4",
            False: "mp3",
        }  # Dictionary of file extensions that correspond to the value of isVideo

        self.clear = lambda: os.system("cls" if os.name == "nt" else "clear")  # Clear the console

        self.YTDL_PATH: str = os.path.join(os.path.dirname(__file__), "bin/yt-dlp.exe")  # Path to the yt-dlp executable
        self.FFMPEG_PATH: str = os.path.join(os.path.dirname(__file__), "bin/ffmpeg.exe")  # Path to the ffmpeg executable

        self.isVideo: bool = True  # Download format: True - mp4, False - mp3
        self.skip_prompts: bool = yes  # Whether or not to skip input prompts with a value of "y"
        self.fallback_input: Exception | None = None  # None if no fallback input has been triggered, otherwise the exception that triggered it

        # if sys.platform == "win32":
        #     pyperclip.set_clipboard("windows")
        # elif sys.platform == "linux":
        #     pyperclip.set_clipboard("xclip")
        # elif sys.platform == "darwin":
        #     pyperclip.set_clipboard("pbobjc")
        # else:  # Unsupported OS
        #     print("Unsupported OS")
        #     sys.exit(1)

        if sys.platform != "win32":
            print("Unsupported OS")
            sys.exit(1)

        if arg_url != "none":
            pyperclip.copy(arg_url)

    def input(self, prompt: str = "", allow_m: bool = False) -> Literal["y", "n", "m"]:
        """Get user input from the keyboard, with traditional input as a fallback

        Args:
            prompt (str): The prompt to give the user
            allow_m (bool): Whether or not `m` is an allowed input/output

        Returns:
            str (y, n, m): The user input, transformed to be one of three single-character strings
        """
        if self.skip_prompts:
            # TODO: logger.debug("Skipping user input with value of 'y'")
            return "y"

        print(prompt)
        unrecog_msg_printed: bool = False
        while True:
            time.sleep(0.35)
            try:
                if self.fallback_input:
                    # If the fallback input was triggered once, then don't bother to try the main input method again
                    raise self.fallback_input
                usr_input = kb.read_event().name
                if usr_input == "Q":
                    # triggering the fallback input manually requires shift+q, so it's unlikely to be pressed by accident
                    raise FallbackInputTrigger
            except Exception as e:
                # TODO: logger.traceback(e)
                if not self.fallback_input:
                    # If the fallback input hasn't been triggered yet, then store the exception that caused it and print a small error message
                    self.fallback_input = e
                    print(f"\n{RED}Failed to read keyboard events due to {type(e).__name__}{NC}")
                usr_input = input(f"{CYAN}Please type your input: {NC}").strip().lower()[0]
            finally:
                # Handle input, either from keyboard event or from user input
                match usr_input:
                    case "enter" | "y":
                        return "y"
                    case "backspace" | "n":
                        return "n"
                    case "m" if allow_m:
                        return "m"
                    case _:
                        if not unrecog_msg_printed and self.fallback_input:
                            # Handle unrecognized fallback input by displaying a message with valid options (only do it once)
                            unrecog_msg = [
                                "\nUnrecognized input, fallback options are:",
                                "Y (Equivalent to Enter)",
                                "N (Equivalent to Backspace)",
                            ]
                            if allow_m:
                                unrecog_msg.append("or M")
                            print(RED + "\n".join(unrecog_msg) + NC)
                            unrecog_msg_printed = True
                            time.sleep(0.5)
                        continue

    def downloadVideo(self, link: str, vidName: str) -> None:
        """Download the target video

        Args:
            link (str): The URL of the media that you want to download
            vidName (str): The name of the media that you want to download
        """
        self.clear()
        targ_folder = "Videos" if self.isVideo else "Music"
        default_cmd = [
            "--ffmpeg-location",
            self.FFMPEG_PATH,
            "-o",
            os.path.expanduser(f"~/{targ_folder}/%(title)s.%(ext)s"),
            link,
        ]
        # Print the name of the to-be downloaded video and its destination
        print(f"{GREEN}Downloading: {vidName} to your {targ_folder} folder\n{NC}")
        # Let the user read the printed line before filling the console with status updates
        time.sleep(1)
        # Setup media downloading command
        if self.isVideo:
            cmd = [
                "--format",
                "bv*[ext=mp4][fps<=60]+ba[ext=m4a]",
            ]
        else:
            cmd = [
                "--extract-audio",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
            ]
        # Run the download command
        # TODO: Capture the command output and display a progress bar-esque message, so the user doesn't have to get exposed to raw command output
        subprocess.run([self.YTDL_PATH] + cmd + default_cmd)
        finished_input = self.input(f"\n{CYAN}Press Enter to exit the program, or Backspace to download another video{NC}")
        if finished_input == "y":
            sys.exit(0)
        else:
            return

    def configDownload(self, link: str) -> None:
        """Here the user can see the video title, choose to download as an mp4 or mp3, and continue or go back

        Args:
            link (str): The URL of the media that you want to download
        """
        self.clear()
        # TODO: Make the processing message have an animated spinner (/,|,\,-)
        print(f"{GREEN}Processing the URL...{NC}", end="\n\n")
        # Process URL to find video name, accounting for errors
        try:
            video_search = subprocess.run([self.YTDL_PATH, "-O", '"%(title)s"', link], capture_output=True, check=True, text=True, timeout=15)
        except Exception as e:
            err_msg = f"{RED}ERROR: "
            # Transform common errors to be user-friendly
            match type(e):
                case subprocess.TimeoutExpired:
                    err_msg += "Video search timed out"
                case subprocess.CalledProcessError:
                    err_msg += "Invalid URL or the video cannot be found"
                case _:
                    # TODO: logger.traceback(e)
                    # TODO: logger.error(e.stderr)
                    err_msg += f"Failed to process URL due to {type(e).__name__} exception"
            error_input = self.input(f"{err_msg}\n{CYAN}Press Enter to exit, or press Backspace to re-scan clipboard{NC}")
            if error_input == "y":
                sys.exit(1)
            else:
                return
        # Display video name and give user some simple options
        videoName = video_search.stdout.strip()
        while True:
            self.clear()
            print(f"{GREEN}Selected video: {videoName}{NC}")
            print(f"{GREEN}Downloading as an {self.EXT_DICT[self.isVideo]}{NC}", end="\n\n")

            config_prompt = ["Enter to download", f"M to switch to {self.EXT_DICT[not self.isVideo]}", "Backspace to re-scan clipboard"]
            user_input = self.input(CYAN + "\n".join(config_prompt) + NC, allow_m=True)
            match user_input:
                case "y":
                    self.downloadVideo(link, videoName)
                    return
                case "m":
                    self.isVideo = not self.isVideo
                    continue
                case "n":
                    return

    def main(self) -> None:
        while True:
            # clear terminal and get clipboard content
            self.clear()
            # TODO: Remove this print statement? Clipboard checks are pretty much instanst
            print(f"{GREEN}Checking user clipboard for a URL...{NC}", end="\n\n")
            url = pyperclip.paste()
            # valid URL check
            if url.startswith("http"):
                self.configDownload(url)
            else:
                # Warn the user if a URL isn't detected and give them the option to continue anyways/retry the download.
                valid_fail = self.input(f"{RED}Valid URL not found. Press Enter to forcefully continue, or Backspace to re-scan clipboard{NC}")
                if valid_fail == "y":
                    self.configDownload(url)
                else:
                    self.clear()
                    time.sleep(0.1)
                    continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        default=False,
        help='Pass a string value of "y" on user input prompts',
    )
    parser.add_argument(
        "--url",
        type=str,
        default="none",
        help="URL of the video to download",
    )
    args = parser.parse_args()

    download = simple_ytdl(args.yes, args.url)
    download.main()
