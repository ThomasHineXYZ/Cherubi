# Shiny Bot

A Python bot based off of the [`discord.py 1.3.4` project](https://discordpy.readthedocs.io/en/v1.3.4/) (this is the current stable release of the project as of time of writing this)
.
## Requirements
1. An [application and bot setup for Discord](https://discord.com/developers/). You'll need the token for it.
<!-- 1. A mysql database with login information to log into a db.
1. A redis database for the user system. -> currently used. -->
1. Python 3.7+ installed

## Instructions
1. Clone this repo into the place you want to run it from.
1. Copy `.env.local.example` to `.env.local` and fill it in with the required values.
1. Run `pip3 install -r requirements.txt` to install all of the required dependancies.
1. Run the main script: `python3 ./bot`.

If you want to overwrite any of the default values (like `MYSQL_PORT`) in `.env` then copy the line and paste it in to your `.env.local` file.

We're licensed under MIT

## Credits
* [BloodyThorn](https://github.com/bloodythorn) and his [WiiHacky](https://github.com/bloodythorn/wiihacky/) project and inspiration to work on this.
* [discord.py](https://github.com/Rapptz/discord.py) for the basis of this project.
* [Lucas's Python.py YouTube Tutorial series](https://www.youtube.com/playlist?list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ) for the help with starting and setting this up.
* [Carberra Tutorials](https://www.youtube.com/playlist?list=PLYeOw6sTSy6ZGyygcbta7GcpI8a5-Cooc) for his tutorials as well

## Donating 💸
Someone mentioned that I should put this here in case people feel like donating a little bit to me and my projects
<a href="https://www.buymeacoffee.com/thomashine" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>
