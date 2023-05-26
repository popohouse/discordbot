This is a heavily modified fork of **https://github.com/AlexFlipnote/discord_bot.py**

Do you need more help? Visit my server here: **https://discord.gg/Yx6dTZvrGr** 

## Requirements
- Python 3.10 and up - https://www.python.org/downloads/
- git - https://git-scm.com/download/
- Discord bot with Message Intent enabled

## Useful to always have
Keep [this](https://discordpy.readthedocs.io/en/latest/) saved somewhere, as this is the docs to discord.py@rewrite.
All you need to know about the library is defined inside here, even code that I don't use in this example is here.


### How to setup with Docker
Docker is an alternative to run the bot 24/7 and always reboot again whenever it crashed. You can find the install manual [here](https://docs.docker.com/install/). This is the suggested method of running the bot.
```
# Build and run the Dockerfile
Rename the file **.env.example** to **.env** filling in required information such as token, reddit information, it's advisded to change default postgres password at least.
docker-compose up -d --build

# Tips on common commands
docker-compose <command>
  ps      Check if bot is online or not (list)
  down    Shut down the bot
  reboot  Reboot the bot without shutting it down or rebuilding
  logs    Check the logs made by the bot.
```

## How to setup without Docker
Note this assumes you have postgres already setup on system. As well requires reddit api key.
1. Make a bot [here](https://discordapp.com/developers/applications/me) and grab the token
![Image_Example1](https://i.ffm.best/koXU1/CaGePINI82.png/raw)

2. Rename the file **.env.example** to **.env** filling in required information such as token, reddit information, and setting postgres info.

3. To install what you need, do **pip install -r requirements.txt**<br>
(If that doesn't work, do **python -m pip install -r requirements.txt**)<br>
`NOTE: Use pip install with Administrator/sudo`

4. Start the bot by having the cmd/terminal inside the bot folder and type **python index.py**

5. You're done, enjoy your bot!



