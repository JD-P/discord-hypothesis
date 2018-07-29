# Discord Hypothesis Bot

This is a [Discord](https://discordapp.com/) bot that tracks and reports activity from a group on the [Hypothesis](https://hypothes.is) annotation web service.

## Installation

Git clone this repository. Then create a virtual environment and install the following libraries:

[python-hypothesis](https://github.com/chaselgrove/python-hypothesis)

[discord.py](https://github.com/Rapptz/discord.py)

Unfortunately discord.py is designed to work with python3 while python-hypothesis
is designed to work with python2, so some 2to3 tweaking was required on my local
copy of the hypothesis library.

I'll probably fix this at some point by either submitting a pull-request to Christian
Haselgrove with python3 compatibility patches, or abandoning the library and doing
the minimal number of features I actually use with [requests](https://github.com/requests/requests) or similar.

### Configuration

Finally, the appropriate API keys need to be added to the json configuration file
included with the bot. Some notes:

* The Hypothesis group ID is not the same as the group name. Group ID's are a
static string of characters that you find in the invite URL before the group
*name*, which is a changable property of the group whereas the ID stays the
same.

* Channels are the *channel id's* that you want to output to. These can be found
as a long string of characters at the end of a Discord URL while viewing the
particular channel you would like the bot to send messages to.
