import discord

from utils import config, data
from utils.database import init_db
config = config.Config.from_env(".env")

#Hardcoded values for which guilds bot is allowed in, simply change this and @bot.check function in order to allow in all, done for while testing/deploying
allowed_guilds = [1034456646614786139]
#kitty kat server only

print("Logging in...")

bot = data.DiscordBot(
    config=config, command_prefix=config.discord_prefix,
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=data.HelpFormat(),
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, users=True
    ),
    intents=discord.Intents(
        # kwargs found at https://docs.pycord.dev/en/master/api.html?highlight=discord%20intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True,
        presences=True, message_content=True,
    )
)

init_db(bot)

@bot.check
async def check_guild(ctx):
    if ctx.guild is None:
        return True
    if ctx.author.id == config.discord_owner_id:
        return True
    if ctx.guild.id in allowed_guilds:
        return True
    await ctx.send("This part of the bot is disabled outside select servers")
    return False

@bot.event 
async def on_ready():
    print(f'{bot.user} is ready!')

try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")