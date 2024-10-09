# simple_ytdl
[![Code style](https://img.shields.io/badge/code_style-black-black?style=for-the-badge)](https://github.com/psf/black)
[![Commit activity](https://img.shields.io/github/commit-activity/t/Jurassic001/simple_ytdl?style=for-the-badge&logo=github)](https://github.com/Jurassic001/simple_ytdl/activity)

### An easy-to-use, text-based program for downloading Youtube videos at high fidelity, utilizing [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [FFmpeg](https://www.ffmpeg.org).

## How to use
### Requirements
This program is compiled on a Windows 10/11 system, so I can only guarantee that it will work on Windows 10/11. If you are using a different operating system, feel free to give it a test run and let me know if it works.

### Installation
Download the latest executable (.exe) file in [releases](https://github.com/Jurassic001/simple_ytdl/releases). <br/>
That's it! You can now run the program and easily download videos at high quality!

### Program Usage
1. Copy the URL of the desired media and run the program.
1. You can choose between .mp4 (video) or .mp3 (audio) format, and the content will be downloaded at 1080p (HD).
    * Download locations are the `Videos` folder for .mp4s and the `Music` folder for .mp3s.
1. The program will also warn you if you try to submit something that doesn't look like a URL (although you can ignore the warning).

### Encountered an issue?
Make a post on the issues tab, detailing what happened, what you were doing when it happened, and what the output of the program was when the issue occurred.

## Contribution guide
If you want to contribute to this project, please feel free to do so! You can make use of the [development scripts](scripts) to help you get started. They're pretty self-explanatory, but if you have any questions, feel free to ask. For the most part, development should be conducted in a virtual environment.

When contributing, make sure to fork the repository and create a pull request with your changes. I'll review it and likely merge it when I get the chance.

## Project ambition
I made this program because I wanted the minimize the brainpower required to download a video. To be honest I don't spend a lot of time downloading videos, so I tend to forget the syntax associated with yt-dlp. This program allows me to quickly and easily download high-quality Youtube videos and audios without any hassle.

I wanted to extend this simplicity to other users, so I redesigned this program to be able to run as an executable file. This way, all someone has to do is download the program and run it, without having to worry about dependencies or syntax.

## Future plans
* Add a GUI to the program
* Add more download location options
* Add workflow tests (need to circumvent Youtube bot checks)

## Legal
### Disclaimer
This program is not affiliated with Youtube, yt-dlp, or FFmpeg. It is an independent project that utilizes these tools to download media. The program is not intended for illegal use, and I am not responsible for any misuse of this program.

### License
You may view the repository's license [here](LICENSE).

### Credits
Executable icon created by [**kliwir art** on Flaticon](https://www.flaticon.com/authors/kliwir-art)
