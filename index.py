import discord
import os
import asyncio
import logging
from typing import Literal, Optional
from discord.ext.commands import Bot, Context, Greedy
from discord.ext import commands, tasks
from utils import config
from datetime import datetime

from utils.database import create_tables, populate_tables
config = config.Config.from_env(".env")


# define bot
bot = Bot(
    config=config, command_prefix=commands.when_mentioned_or(config.discord_prefix),
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, users=True
    ),
    intents=discord.Intents.all()
)
bot.uptime = datetime.utcnow()
bot.config = config

#load the commands
async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                logging.info(f"Loaded extension '{extension}'")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                logging.error(f"Failed to load extension {extension}\n{exception}")
                print(f"Failed to load extension {extension}\n{exception}")


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

#Runs when bot is ready
@bot.event 
async def on_ready():
    print(f'{bot.user} is ready!')
    await create_tables()
    await populate_tables(bot)
    await load_cogs()

try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")