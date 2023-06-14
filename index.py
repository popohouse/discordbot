import discord
import os
import logging
from typing import Literal, Optional
from discord.ext.commands import Bot, Context, Greedy
from discord.ext import commands
from utils import config
import time
import asyncpg
import signal
import asyncio
from utils.database import create_tables, populate_tables

config = config.Config.from_env(".env")


# define bot
bot = Bot(
    config=config, command_prefix=commands.when_mentioned_or(config.discord_prefix),
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=True, users=True
    ),
    intents=discord.Intents.all()
)


# load the commands
async def load_cogs() -> None:
    """The code in this function is executed whenever the bot will start."""
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                logging.info("Loaded extension '%s'", extension)
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                logging.error("Failed to load extension '%s'", exception)
                print(f"Failed to load extension {extension} {exception}")


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
        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
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


# Runs when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')
    bot.pool = await asyncpg.create_pool(
            user=config.postgres_user,
            password=config.postgres_password,
            database=config.postgres_database,
            host=config.postgres_host,
            command_timeout=30
        )
    await create_tables(bot)
    await populate_tables(bot)
    await load_cogs()
    if not hasattr(bot, "uptime"):
        bot.uptime = time.time()


logging.getLogger('asyncio').setLevel(logging.DEBUG)


async def main():
    # Signal handler
    def signal_handler(sig, frame):
        print('Caught signal, shutting down...')
        asyncio.create_task(shutdown(sig, frame))

    async def shutdown(sig, frame):
        # Unload all cogs
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.unload_extension(f"cogs.{extension}")
                    logging.info("Unloaded extension '%s'", extension)
                    print(f"Unloaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    logging.error("Failed to unload extension '%s'", exception)
                    print(f"Failed to unload extension {extension} {exception}")
        await bot.pool.close()
        await bot.close()
        os.exit(0)
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        await bot.close()


asyncio.run(main())