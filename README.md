# RssDownloader

With this simple RssDownloader, you can parse your favorite RSS feeds and download its linked content. It will not download files that are already present in the download directory, so it can safely be run often. It is written in Python 3, and can be run on both Windows, Linux and MacOS. The easiest way to run it regularly is through crontab or a similar scheduler. 

## Installation

Clone this repository anywhere on your machine, e.g.

    cd ~/
    git clone https://github.com/blixhavn/RssDownloader.git

Enter the project folder create a python virtual environment

    cd RssDownloader
    python3 -m venv venv

Activate the virtual environment and install the dependencies. Activation is a little different in windows, google it if you need to.

    source venv/bin/activate
    pip install -r requirements.txt



### Configuration options

The configuration is written as a list of JSON objects, with each object containing a link to the RSS feed, and categories with a regex expression for matching on the _title_ tag of each item, and a directory to save the linked resource. Example:

    [{
        "rss": "https://podkast.nrk.no/program/p2-serier.rss",
        "categories": {
            "Sammen med Sandvik": {
                "regex": "^Sammen med Sandvik:",
                "directory":  "./podcasts/sammen"
            },
            "Norgeshistorie": {
                "regex": "^Norgeshistorie:",
                "directory":  "./podcasts/norgeshistorie"
            }
        }
    }]

**Note**: The regex matching is case insensitive.

The category names are not used for anything in particular at the moment, other than debug messages.

### Scheduling

In linux, the easiest way to schedule this is using crontab. In a terminal, write `crontab -e` to bring up the editor. Then, use the full path to both the virtual environment Python binary, and the script itself, e.g:

    */30 * * * * /home/user/RssDownloader/venv/bin/python3 /home/user/RssDownloader/RssDownloader.py

[Crontab.guru](https://crontab.guru/) is helpful for writing the scheduling pattern.

### Troubleshooting

If the script isn't working as intended, check the `debug.log` file for errors. You can also run the script with a `--debug` flag for more verbose information.


## Further plans
As I made this script for my own specific need, I don't have any great visions of improving its functionality. If you need a full fledged download utility, [FlexGet](https://flexget.com/) might be a better alternative for you. However, some adjustments and improvements can of course be done - especially to handle variations of providing resource links, which I have seen two options for so far.


## Feedback and contributions
If you have any feedback, questions or suggestions, do not hesitate to make an issue on GitHub 🙂 Also, feel free to make contributions in form of pull requests!


## License 
RssDownloader is released under the MIT license. Have at it.

-----
Made by Øystein Blixhavn