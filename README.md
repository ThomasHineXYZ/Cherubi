[![shield.io](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-364/)

# Cherubi

Cherubi is a bot to add a little bit of fun and friendly rivalry to Pokémon GO Discord communities.

It is a Python bot based off of the [`discord.py 1.3.4` project](https://discordpy.readthedocs.io/en/v1.3.4/) (this is the current stable release of the project as of time of writing this).

[Here's the invite link for the bot](https://discordapp.com/oauth2/authorize?client_id=741194655680561172&scope=bot&permissions=268823632)
## Requirements
1. An [application and bot setup for Discord](https://discord.com/developers/) (You'll need the token for it).
1. MariaDB (or MySQL) database.
1. Redis
1. Python 3.7+ and PIP

## Instructions
1. Clone this repo into the place you want to run it from.
1. Copy `.env.local.example` to `.env.local` and fill it in with the required values.
1. Run `pip3 install -r requirements.txt` to install all of the required dependancies.
1. Run the main script: `python3 ./bot`.

For setting up the MySQL / MariaDB privileges: `GRANT SELECT, INSERT, UPDATE, DELETE ON <table_name>.* TO '<user_name>'@'localhost';`

If you want to overwrite any of the default values (like `MYSQL_PORT`) in `.env` then copy the line and paste it in to your `.env.local` file.

We're licensed under MIT.

## Directions for using Cherubi:
By default the command prefix for Cherubi is `!`, but this can be changed (as you'll see below) on a server-by-server basis. So keep that in mind when reading the list of commands below.<br/>
For DMing the bot though, any of `!`, `.`, `?`, `$`, `%`, `:`, `;`, `>` will work as the command prefix. It is also set up that if no command prefix is given, then it'll still run the command (ex: `help` vs `!help`).<br/>
If you run `!help` on a server where the command prefix isn't set as `!` then it'll show a message of how to run help. This is in case you forget what you set your command prefix as.<br/>

Arguments within \< \> are required.<br/>
Arguments within \[ \] are optional.

### Friend Code Commands
`!friendcode` is aliased as `!fc`, so you can use them interchangeably.
| Command                                          | Requirements    | Description                                                                       |
| --------                                         | :-------------: | ------------                                                                      |
| **!friendcode**                                  | -               | Sends embed messages for each of the friend codes on your list.                   |
| **!friendcode** \[tagged user\]                  | -               | If you tag a user it'll do the same but with their codes.                         |
| **!friendcode** \[filter\]                       | -               | If you add in a filter text. Can be combined with a tagged user if desired.       |
| **!friendcode add** \<username\> \<friend code\> | -               | Adds / edits a friend code on your list.                                          |
| **!friendcode list**                             | -               | This lists all of your friend codes in a single message. **Not mobile friendly.** |
| **!friendcode listall**                          | _Server Owner_  | Lists all friend codes for everyone on your server. **Not mobile friendly.**      |
| **!friendcode remove** \<username\>              | -               | Removes a friend code from your list.                                             |
| **!friendcode visibility**                       | -               | If run on its own, it'll tell you your current visibility setting.                |
| **!friendcode visibility** \<setting\>           | -               | Sets your visibility as you wish. The options are public, private, and hidden.    |

### Leaderboard Commands
| Command                              | Requirements    | Description                                                                             |
| --------                             | :-------------: | ------------                                                                            |
| **!sethome**                         | -               | Sets your home server.                                                                  |
| **!leaderboard shiny**               | -               | Brings up the leaderboard for your server. **Not mobile friendly.**                     |
| **!leaderboard shiny** \[\-\-global] | -               | If `--global` is given, it'll bring up the global leaderboard. **Not mobile friendly.** |

### Shiny Checklist Commands
| Command                                  | Requirements    | Description                                                        |
| --------                                 | :-------------: | ------------                                                       |
| **!shiny add** \<pokemon\>               | -               | Adds one of the given Pokémon to your checklist.                   |
| **!shiny add** \<pokemon\> \[number\]    | -               | If a number is given, it'll add that many of the given Pokémon.    |
| **!shiny list**                          | -               | Prints out your shiny list.                                        |
| **!shiny remove** \<pokemon\>            | -               | Removes one of the given Pokémon from your checklist.              |
| **!shiny remove** \<pokemon\> \[number\] | -               | If a number is given, it'll remove that many of the given Pokémon. |

### Owner
| Command                         | Requirements    | Description                                           |
| --------                        | :-------------: | ------------                                          |
| **!changeprefix** \<character\> | _Server Owner_  | Changes the command prefix to a new single character. |
| **!serverinfo**                 | _Server Owner_  | Gives an readout for some stats on the server.        |
| **!userinfo**                   | _Server Owner_  | Gives some stats for a tagged user.                   |

### Miscellaneous Commands
| Command                | Requirements    | Description                                                                                    |
| --------               | :-------------: | ------------                                                                                   |
| **!b** \[message\]     | -               | Translates to a [B-Button message](https://knowyourmeme.com/memes/b-button-emoji-%F0%9F%85%B1) |
| **!emoji** \[message\] | -               | Translates messages to emoji characters.                                                       |
| **!f**                 | -               | [Let's get an `f` in chat.](https://knowyourmeme.com/memes/press-f-to-pay-respects)            |
| **!help** \[command\]  | -               | Shows bot/command help, with descriptions.                                                     |
| **!hi**                | -               | Why not say hi to Cherubi? She's friendly.                                                     |
| **!ping**              | -               | Runs a heartbeat check on the bot. PONG!                                                       |

### Temporary / Test Commands
These are commands that are currently implemented, but might change or be removed
| Command                      | Requirements    | Description                           |
| --------                     | :-------------: | ------------                          |
| **!normalembed** \<pokemon\> | -               | Shows you info about a Pokémon.       |
| **!shinyembed** \<pokemon\>  | -               | Shows you info about a shiny Pokémon. |


## Credits
* [BloodyThorn](https://github.com/bloodythorn) and his [WiiHacky](https://github.com/bloodythorn/wiihacky/) project for the inspiration to work on this.
* [discord.py](https://github.com/Rapptz/discord.py) for the basis of this project.
* [Lucas's Python.py YouTube Tutorial series](https://www.youtube.com/playlist?list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ) for the help with starting and setting this up.
* [Carberra Tutorials](https://www.youtube.com/playlist?list=PLYeOw6sTSy6ZGyygcbta7GcpI8a5-Cooc) for his tutorials as well

## Donating
Someone mentioned that I should put this here in case people feel like donating a little bit to me and my projects

[![shield.io](https://img.shields.io/badge/buymeacoffee-thomashine-blue)](https://www.buymeacoffee.com/thomashine)
