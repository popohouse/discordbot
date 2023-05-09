import discord

from utils import config, data
from utils.database import create_tables, populate_tables, removed_while_offline, on_guild_remove, on_guild_join
config = config.Config.from_env(".env")

#Hardcoded values for which guilds bot is allowed in, simply change this and @bot.check function in order to allow in all, done for while testing/deploying
allowed_guilds = [1034456646614786139]
#kitty kat server only

create_tables()

print("Logging in...")

bot = data.DiscordBot(
    config=config, command_prefix=config.discord_prefix,
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=data.HelpFormat(),
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, users=True
    ),
    intents=discord.Intents.all()
)



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
    populate_tables(bot)
    removed_while_offline(bot)

bot.add_listener(on_guild_remove)
bot.add_listener(on_guild_join)

try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")