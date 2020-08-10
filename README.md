[![shield.io](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-364/)
[![shield.io](https://img.shields.io/badge/support-discord-lightgrey.svg)](https://discord.gg/hhVjAN8)

# Cherubi

Cherubi is a bot to add a little bit of fun and friendly rivalry to Pokémon GO Discord communities.

It is a Python bot based off of the [`discord.py 1.3.4` project](https://discordpy.readthedocs.io/en/v1.3.4/) (this is the current stable release of the project as of time of writing this).

[Here's the invite link for the bot](https://discordapp.com/oauth2/authorize?client_id=741194655680561172&scope=bot&permissions=268823632)
## Requirements
1. An [application and bot setup for Discord](https://discord.com/developers/) (You'll need the token for it).
1. A MariaDB (or MySQL) database.
1. Python 3.7+ installed
1. PIP for Python 3

## Instructions
1. Clone this repo into the place you want to run it from.
1. Copy `.env.local.example` to `.env.local` and fill it in with the required values.
1. Run `pip3 install -r requirements.txt` to install all of the required dependancies.
1. Run the main script: `python3 ./bot`.

For setting up the MySQL / MariaDB privileges: `GRANT SELECT, INSERT, UPDATE, DELETE ON <table_name>.* TO '<user_name>'@'localhost';`

If you want to overwrite any of the default values (like `MYSQL_PORT`) in `.env` then copy the line and paste it in to your `.env.local` file.

We're licensed under MIT

## Directions for using Cherubi:
By default the command prefix for Cherubi is `!`, but this can be changed (as you'll see below) on a server-by-server basis. So keep that in mind when reading the list of commands below.<br/>
For DMing the bot though, any of `!`, `.`, `?`, `$`, `%`, `:`, `;`, `>` will work as the command prefix. It is also set up that if no command prefix is given, then it'll still run the command (ex: `help` vs `!help`).

Arguments within \< \> are required.<br/>
Arguments within \[ \] are optional.

### Leaderboard Commands
| Commands                             | Requirements    | Description                                                   |
| --------                             | :-------------: | ------------                                                  |
| **!sethome**                         | -               | Sets your home server.                                        |
| **!leaderboard shiny**               | -               | Brings up the leaderboard for your server.                    |
| **!leaderboard shiny** \[\-\-global] | -               | If `--global` is given, it'll bring up the global leaderboard |

### Shiny Checklist Commands
| Commands                             | Requirements    | Description                                                       |
| --------                             | :-------------: | ------------                                                      |
| **!shiny add** \<pokemon\>             | -               | Adds one of the given Pokémon to your checklist                   |
| **!shiny add** \<pokemon\> [number]    | -               | If a number is given, it'll add that many of the given Pokémon    |
| **!shiny list**                      | -               | Prints out your shiny list                                        |
| **!shiny remove** \<pokemon\>          | -               | Removes one of the given Pokémon from your checklist              |
| **!shiny remove** \<pokemon\> [number] | -               | If a number is given, it'll remove that many of the given Pokémon |

### Owner
| Commands                      | Requirements    | Description                                          |
| --------                      | :-------------: | ------------                                         |
| **!changeprefix** \<character\> | _Server Owner_  | Changes the command prefix to a new single character |
| **!serverinfo**               | _Server Owner_  | Gives an readout for some stats on the server        |
| **!userinfo**                 | _Server Owner_  | Gives some stats for a tagged user                   |

### Miscellaneous Commands
| Commands              | Requirements    | Description                                |
| --------              | :-------------: | ------------                               |
| **!help** \[command\] | -               | Shows bot/command help, with descriptions. |
| **!ping**             | -               | Runs a heartbeat check on the bot. PONG!   |

### Temporary / Test Commands
These are commands that are currently implemented, but might change or be removed
| Commands               | Requirements    | Description                          |
| --------               | :-------------: | ------------                         |
| !normalembed \<pokemon\> | -               | Shows you info about a Pokémon       |
| !shinyembed \<pokemon\>  | -               | Shows you info about a shiny Pokémon |


## Credits
* [BloodyThorn](https://github.com/bloodythorn) and his [WiiHacky](https://github.com/bloodythorn/wiihacky/) project for the inspiration to work on this.
* [discord.py](https://github.com/Rapptz/discord.py) for the basis of this project.
* [Lucas's Python.py YouTube Tutorial series](https://www.youtube.com/playlist?list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ) for the help with starting and setting this up.
* [Carberra Tutorials](https://www.youtube.com/playlist?list=PLYeOw6sTSy6ZGyygcbta7GcpI8a5-Cooc) for his tutorials as well

## Donating
Someone mentioned that I should put this here in case people feel like donating a little bit to me and my projects

[![shield.io](https://img.shields.io/badge/buymeacoffee-thomashine-blue)](https://www.buymeacoffee.com/thomashine)
