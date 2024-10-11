import argparse
import os
import sys
import time

import pyperclip
import yt_dlp


class simple_ytdl:
    def __init__(self, skip: bool, skip_val: str, arg_url: str) -> None:
        self.EXT_DICT: dict[bool, str] = {
            True: "mp4",
            False: "mp3",
        }  # Dictionary of file extensions that correspond to the value of isVideo

        self.clear = lambda: os.system("cls" if os.name == "nt" else "clear")  # Clear the console

        self.isVideo: bool = True  # Download format: True - mp4, False - mp3
        self.skip_prompts: bool = skip  # Skip input prompts
        self.prompt_skip_val: str = skip_val  # Value to return when skipping prompts

        if sys.platform == "win32":
            pyperclip.set_clipboard("windows")
        elif sys.platform == "linux":
            pyperclip.set_clipboard("xclip")
        elif sys.platform == "darwin":
            pyperclip.set_clipboard("pbobjc")
        else:  # Unsupported OS
            print("Unsupported OS")
            sys.exit(1)

        if arg_url != "none":
            pyperclip.copy(arg_url)

    def input(self, prompt: str = "") -> str:
        """Prompt the user for input, or skip the prompt if the relevant argument is applied

        Args:
            prompt (str): The prompt to display to the user

        Returns:
            str: The user's input, or the value returned when skipping prompts
        """
        if self.skip_prompts:
            return self.prompt_skip_val
        else:
            return input(prompt).strip().lower()

    def downloadVideo(self, link: str, vidName: str) -> None:
        """Download the target video

        Args:
            link (str): The URL of the media that you want to download
            vidName (str): The name of the media that you want to download
        """
        # Print the name of the to-be downloaded video and its destination
        self.clear()
        targ_folder = "Videos" if self.isVideo else "Music"
        print(f"Downloading: {vidName} to your {targ_folder} folder\n")
        # Let the user read the printed line before filling the console with status updates
        time.sleep(1)
        # Start downloading the video
        ydl_opts = {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" if self.isVideo else "ba[ext=mp3]/b",
            "outtmpl": os.path.expanduser(f"~/{'Videos' if self.isVideo else 'Music'}/%(title)s.%(ext)s"),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        self.input("\nPress Enter to exit the program")
        sys.exit(0)

    def configDownload(self, link: str) -> None:
        """Here the user can see the video title, choose to download as an mp4 or mp3, and continue or go back

        Args:
            link (str): The URL of the media that you want to download
        """
        self.clear()
        print("Processing the URL...", end="\n\n")
        try:
            title_check_options = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "force_generic_extractor": True,
                "outtmpl": "%(title)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(title_check_options) as title_checker:
                info_dict = title_checker.extract_info(link, download=False)
                videoName: str = info_dict["title"].strip().strip(".")  # type: ignore
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            self.input(f"Press Enter to try again. ")
            return
        while True:
            self.clear()
            print(f"Selected video: {videoName}")
            print(f"Downloading as an {self.EXT_DICT[self.isVideo]}", end="\n\n")

            print("Type anything to confirm and download the video")
            print(f'Type "S" to switch to {self.EXT_DICT[not self.isVideo]}')
            print('Type "N" to go back')
            time.sleep(0.5)
            user_input = self.input()
            if user_input.startswith("s"):
                self.isVideo = not self.isVideo
            elif user_input.startswith("n"):
                return
            else:
                self.downloadVideo(link, videoName)

    def main(self) -> None:
        while True:
            # clear terminal and get clipboard content
            self.clear()
            print("Checking user clipboard for a URL...", end="\n\n")
            url = pyperclip.paste()
            # valid URL check
            if url.startswith("http"):
                self.configDownload(url)
            else:
                # Warn the user if a URL isn't detected and give them the option to continue anyways/retry the download.
                valid_fail = self.input("Valid URL not found. Do you want to continue? (y/n) ")
                time.sleep(0.5)
                if valid_fail.startswith("n"):
                    continue
                else:
                    self.configDownload(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip",
        action="store_true",
        default=False,
        help="Skip input prompts and use default values",
    )
    parser.add_argument(
        "--skip-val",
        type=str,
        default="",
        help="Value to return when skipping prompts",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="none",
        help="URL of the video to download",
    )
    args = parser.parse_args()

    download = simple_ytdl(args.skip, args.skip_val, args.url)
    download.main()
