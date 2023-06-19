import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
from utils import permissions

cooldowns = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.user)


class Leveling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cache = {}
        self.leveling_cache = {}
        self.update_database_task.start()

    async def cog_unload(self):
        self.update_database_task.cancel()
        await self.update_database()

    @tasks.loop(minutes=2)
    async def update_database_task(self):
        print("Updating database")
        await self.update_database()

    async def save_data(self):
        await self.update_database()

    async def setup(self):
        await self.load_leveling_cache()

    async def load_leveling_cache(self):
        print("Loading leveling cache")
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                query = "SELECT guild_id, user_id, xp FROM leveling"
                rows = await conn.fetch(query)
                for row in rows:
                    guild_id = row["guild_id"]
                    user_id = row["user_id"]
                    xp = row["xp"]
                    self.leveling_cache[(guild_id, user_id)] = xp
                    print(f"Loaded {xp} xp for user {user_id} in guild {guild_id}.")

    async def update_leveling_cache(self, guild_id, user_id, xp):
        if user_id is None:
            if (guild_id, None) in self.leveling_cache:
                del self.leveling_cache[(guild_id, None)]
        else:
            self.leveling_cache[(guild_id, user_id)] = xp

    async def update_database(self):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                for (guild_id, user_id), xp in self.leveling_cache.items():
                    query = "INSERT INTO leveling (guild_id, user_id, xp) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET xp = $3"
                    await conn.execute(query, guild_id, user_id, xp)

    @app_commands.command()
    async def level(self, interaction: discord.Interaction):
        """Enables or disables level tracking"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}): 
            return
        guild_id = interaction.guild.id
        bot_user_id = self.bot.user.id
        async with self.bot.pool.acquire() as conn:
            await conn.execute("INSERT INTO leveling (guild_id, user_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", guild_id, interaction.user.id)
        await self.update_leveling_cache(guild_id, interaction.user.id, 0)
        await interaction.response.send_message("Leveling is now enabled in this server.", ephemeral=True)


    @app_commands.command()
    async def rank(self, interaction: discord.Interaction):
        """Shows your current level."""
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        if not any(key[0] == guild_id for key in self.leveling_cache):
            return await interaction.response.send_message("Leveling is not enabled in this server.", ephemeral=True)
        if (guild_id, user_id) not in self.leveling_cache:
            return await interaction.response.send_message("You have no xp.", ephemeral=True)
        if (guild_id, user_id) in self.leveling_cache:
            xp = self.leveling_cache[(guild_id, user_id)]
            level = int(xp ** (1/4))
            await interaction.response.send_message(f"You are level {level} with {xp} xp.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        user_id = message.author.id
        if any(key[0] == guild_id for key in self.leveling_cache):
            print("guild in cache")
            xp = self.leveling_cache.get((guild_id, user_id), 0)
            xp += 1
            await self.update_leveling_cache(guild_id, user_id, xp)
            print(f"User {user_id} in guild {guild_id} now has {xp} xp.")


async def setup(bot):
    leveling_cog = Leveling(bot)
    await leveling_cog.setup()
    await bot.add_cog(leveling_cog)
