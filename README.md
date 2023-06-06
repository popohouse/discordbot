This is a heavily modified fork of **https://github.com/AlexFlipnote/discord_bot.py**

Currently WIP, features half implemented and cogs half done. I have an internal list of features/plans for cog modifications I plan to share.

Do you need more help? Visit my server here: **https://discord.gg/Yx6dTZvrGr** 

# Requirements 
- Python 3.10 and up - https://www.python.org/downloads/
- git - https://git-scm.com/download/
- Discord bot with Message Intent enabled [here](https://discordpy.readthedocs.io/en/stable/discord.html)
- Docker if wanting longer uptime
- Poe api key, Find how to get it [here](https://github.com/ading2210/poe-api#finding-your-token)
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


# Current features

## Commands
Admin cog

    amiadmin - Check if you are bot owner.
    load - Load a cog.
    unload - Unload a cog.
    reload - Reloads a cog.
    reloadall -Reloads all cogs.
    reloadutils - Reloads a utils module.
    dm - Direct message a user.
Anilist cog

    anime - Check info on anime.
    manga - Check info on manga.
Animal cog

    Animal - Post animal type of subcommand choice
        dog
        cat
        duck
        hamster
        fox
Birthday cog

    setbirthday - Set your birthday
    birthdayrole - Set role user should get midnight on their birthday
    birthdaychannel - Set channel where bot should wish users happy birthday at midnight on their birthday
Conversion cog

    Convert - Converts between two values
Dailycat cog

    dailycat - Set where dailycat pic should be posted
Discord cog

    avatar - get avatar of user
    mods - list current online mods
Fun cog

    rate - Rates random thing
    f - Pay respect to what you wish
    eightball - Consult 8ball to receive an answer
    catmeme - Random cat meme 
    coffee - Random coffee image
    urban - get definition for word from urban dictionrary
    coinflip - flip a coin
    reverse - reverses text 
    password - get password 
    hotcalc - Rates how hot a discord user is
    noticeme - posts gif
    dice - dice game
    inspire - become inspired 
Info cog

    ping - pong
    invite - invite me to your server
    botserver - get invite link to bot support server
    covid - get covid stats for country
    about - info about bot  
Logging cog

    Log message edit
    Log message delete
    Log nickname changes
Love cog

    kiss - be actioned or action user
    hug - be actioned or action user
    bonk - be actioned or action user
    slap - be actioned or action user
    wink - be actioned or action user
    pat - be actioned or action user
Mod cog

    Timeout - timeout user
    Kick - kick user
    modrole - set mod role which can run most mod actions
    addrole - add a role to user
    delrole - remove role from user
    massrole - add role to all users
    massunrole - remove role from all users
Reaction role cog

    reactionrole - Create reaction role on existing message.
Story cog

    story - Used for one word story channels, gets all current message and sends in nice .txt file as current "complete" story
Timezone

    settime - Set your timezone
    time - Get time of yourself or user
    deltime - Remove your timezone
## Misc
Any metion of bot is passed to poe.com ai for gpt responses.
