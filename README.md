This is a heavily modified fork of **https://github.com/AlexFlipnote/discord_bot.py**

Do you need more help? Visit my server here: **https://discord.gg/Yx6dTZvrGr** 

## Requirements 
- Python 3.10 and up - https://www.python.org/downloads/
- git - https://git-scm.com/download/
- Discord bot with Message Intent enabled [here](https://discordpy.readthedocs.io/en/stable/discord.html)
- Reddit api key [here](https://www.reddit.com/prefs/apps)
- Docker if wanting longer uptime
## Useful to always have
Keep [this](https://discordpy.readthedocs.io/en/latest/) saved somewhere, as this is the docs to discord.py@rewrite.
All you need to know about the library is defined inside here, even code that I don't use in this example is here.


# Steup
## Docker setup

1. Rename the file **.env.example** to **.env** filling in required information such as token, reddit information, it's advisded to change default postgres password at least.

2. docker-compose up -d --build


## Non docker setup
Note this assumes you have postgres already setup on system.

1. Rename the file **.env.example** to **.env** filling in required information such as token, reddit information, and setting postgres info.

2. To install what you need, do **pip install -r requirements.txt**<br>
(If that doesn't work, do **python -m pip install -r requirements.txt**)<br>
`NOTE: Use pip install with Administrator/sudo`

3. Start the bot by having the cmd/terminal inside the bot folder and type **python index.py**

4. You're done, enjoy your bot!



