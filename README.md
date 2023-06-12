This is a heavily modified fork of **https://github.com/AlexFlipnote/discord_bot.py**

Currently WIP, track progress of WIP features here **https://trello.com/b/UNOVi7RJ/discordbot**

Implemented features found here **https://bin.ffm.best/popo/9845fd1e359c4439871fe156fc1c4673**

Do you need more help? Visit my server here: **https://discord.gg/Yx6dTZvrGr** 

# Project Requirements 
Before running the project, you will need the following
- git - https://git-scm.com/download/
- Discord bot with Message Intent enabled [here](https://discordpy.readthedocs.io/en/stable/discord.html)
- Poe api key, Find how to get it [here](https://github.com/ading2210/poe-api#finding-your-token)

# Docker hosted
- Docker 

# Non docker 
- Postgres database
- Python 3.10 and up - https://www.python.org/downloads/

# Setup
## Running with Docker
If you choose to run the bot using Docker, the setup process is simplified. Follow the steps below:
1. Rename the file **.env.example** to **.env** filling in required information such as discord token, poe token,  It is advised to change the default password for the PostgreSQL database.

2. Run the following command to start the Docker containers: **docker-compose up -d --build**

## Non docker setup
If you prefer to run the bot without Docker, follow these steps:<br>
`Note: This assumes you have already set up a PostgreSQL database on your system.`

1. Rename the file **.env.example** to **.env** and fill in the required information, such as your Discord token, Poe token, and PostgreSQL details.

2. Install the project dependencies by running the following command: **pip install -r requirements.txt**<br>
(If that doesn't work, do **python -m pip install -r requirements.txt**)<br>

3. Start the bot by navigating to the bot folder in your command prompt or terminal and running the following command: **python index.py**

4. You're done, enjoy your bot!