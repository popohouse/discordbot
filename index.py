import discord

from utils import default
from utils.data import Bot, HelpFormat

#Hardcoded values for which guilds bot is allowed in, simply remove this and @bot.check function in order to allow in all, done for while testing/deploying
allowed_guilds = [1034456646614786139, 914431811461984266, 1099621557128671303]
#kitty kat, popo house, popo support server
config = default.load_json()
print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents.all()
)

@bot.check
async def check_guild(ctx):
    if ctx.guild.id not in allowed_guilds:
        await ctx.send("This part of the bot is disabled outside select servers")
        return False
    return True

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")