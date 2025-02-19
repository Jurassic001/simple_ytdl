import argparse
import os
import subprocess
import sys
import threading
import time
import traceback
from typing import Literal

import keyboard as kb
import pyperclip
from loguru import logger

RED: str = "\033[0;31m"  # Used for error msgs and problem reports
GREEN: str = "\033[0;32m"  # Used for success/info messages
CYAN: str = "\033[0;36m"  # Used for user input prompts
NC: str = "\033[0m"  # No color

# Used ONLY for download status messages
YELLOW: str = "\033[0;33m"
BLUE: str = "\033[0;94m"


class FallbackInputTrigger(Exception):
    """Exception to trigger the fallback input method manually"""

    def __init__(self, key_name: str) -> None:
        if key_name.isupper():
            # Convert uppercase keypress names to shift+lowercase key
            key_name = f"shift+{key_name.lower()}"
        super().__init__(f'Fallback input method triggered by manual user input ("{key_name}" keypress)')


class simple_ytdl:
    def __init__(self, yes: bool, verbose: bool, arg_url: str) -> None:
        self.EXT_DICT: dict[bool, str] = {
            True: "mp4",
            False: "mp3",
        }  # Dictionary of file extensions that correspond to the value of isVideo

        self.clear = lambda: os.system("cls" if os.name == "nt" else "clear")  # Clear the console

        self.YTDL_PATH: str = os.path.join(os.path.dirname(__file__), "bin/yt-dlp.exe")  # Path to the yt-dlp executable
        self.FFMPEG_PATH: str = os.path.join(os.path.dirname(__file__), "bin/ffmpeg.exe")  # Path to the ffmpeg executable

        self.isVideo: bool = True  # Download format: True - mp4, False - mp3
        self.verbose: bool = verbose  # Whether or not to enable verbose logging
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

        # Logger setup
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "level": "TRACE" if self.verbose else "ERROR",
                    "format": "<r><b>{level}</b></r> on <c>{function}</c>:<c>{line}</c> after <g>{elapsed.seconds} second(s)</g> - <r>{message}</r>",
                }
            ]
        )

    def input(self, prompt: str = "", allow_m: bool = False) -> Literal["y", "n", "m"]:
        """Get user input from the keyboard, with traditional input as a fallback

        Args:
            prompt (str): The prompt to give the user
            allow_m (bool): Whether or not `m` is an allowed input/output

        Returns:
            str (y, n, m): The user input, transformed to be one of three single-character strings
        """
        if self.skip_prompts:
            logger.info("Skipping user input with value of 'y'")
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
                    raise FallbackInputTrigger(usr_input)
            except Exception as e:
                logger.trace(traceback.format_exc())
                if not self.fallback_input:
                    # If the fallback input hasn't been triggered yet, then store the exception that caused it and print a small error message
                    self.fallback_input = e
                    logger.error(e)
                usr_input = input(f"{CYAN}Please type your input: {NC}").strip().lower()[0]
            finally:
                # Handle input, either from keyboard event or from user input
                logger.info(f'Raw input is: "{usr_input}"')
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

    def _url_proc_msg(self) -> None:
        """URL processing message with a simple animation"""
        base_msg = f"\r{GREEN}Processing the URL"
        while True:
            for frame in [".  ", ".. ", "...", "   "]:
                if not self.url_processing:
                    print()  # Create newline after processing is done
                    return
                sys.stdout.write(base_msg + frame)
                sys.stdout.flush()
                time.sleep(0.4)

    def downloadVideo(self, link: str, vidName: str) -> None:
        """Download the target video

        Args:
            link (str): The URL of the media that you want to download
            vidName (str): The name of the media that you want to download
        """
        # Download process setup
        self.clear()
        targ_folder = "Videos" if self.isVideo else "Music"
        progress_template = f"{BLUE}Download Completion: %(progress._percent_str)s || {YELLOW}Time Remaining: %(progress._eta_str)s{NC}"
        print(f"{GREEN}Downloading: {vidName} to your {targ_folder} folder{NC}")

        # universal yt-dlp arguments (appended to specific args because the URL must be the last yt-dlp argument)
        default_cmd = [
            "--ffmpeg-location",
            self.FFMPEG_PATH,
            "-o",
            os.path.expanduser(f"~/{targ_folder}/%(title)s.%(ext)s"),
            "--verbose" if self.verbose else "--quiet",
            "--progress",
            "--progress-template",
            progress_template,
            link,
        ]
        # extension specific yt-dlp arguments
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
        try:
            subprocess.run([self.YTDL_PATH] + cmd + default_cmd, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            logger.trace(traceback.format_exc())
            logger.debug(e.stderr)
            logger.error(f"Download failed with return code {e.returncode}")
        else:
            logger.success("Download completed successfully!")
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
        self.url_processing: bool = True
        logger.info("Attempting to find video name using yt-dlp")
        processing_animation = threading.Thread(target=self._url_proc_msg, daemon=True)
        processing_animation.start()
        # Process URL to find video name, accounting for errors
        try:
            video_search = subprocess.run([self.YTDL_PATH, "-O", '"%(title)s"', link], capture_output=True, check=True, text=True, timeout=15)
            self.url_processing: bool = False
            processing_animation.join()
            logger.success("Video name found!")
        except Exception as e:
            self.url_processing: bool = False
            processing_animation.join()
            # Transform common errors to be user-friendly
            match type(e):
                case subprocess.TimeoutExpired:
                    err_msg = "Video search timed out"
                case subprocess.CalledProcessError:
                    err_msg = "Invalid URL or the video cannot be found"
                case _:
                    err_msg = f"Failed to process URL due to {type(e).__name__} exception"
            logger.trace(traceback.format_exc())
            logger.error(err_msg)
            error_input = self.input(f"{CYAN}Press Enter to exit, or press Backspace to re-scan clipboard{NC}")
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

    @logger.catch(
        level="CRITICAL",
        message="A critical error has occurred, please copy this output and report this error to https://github.com/Jurassic001/simple_ytdl/issues",
    )
    def main(self) -> None:
        while True:
            # clear terminal and get clipboard content
            self.clear()
            logger.info("Checking user clipboard for a URL")
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
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="none",
        help="URL of the video to download",
    )
    args = parser.parse_args()

    download = simple_ytdl(args.yes, args.verbose, args.url)
    download.main()
