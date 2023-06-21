import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
from utils import permissions
import  math
cooldowns = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.user)

class Buttons(discord.ui.View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.current_page = 0
        self.page_counter = None
        # Remove buttons and page counter if there is only one page
        if len(self.pages) <= 1:
            self.clear_items()
            self.page_counter = None  # Set page_counter to None

    def update_page_counter(self):
        if self.page_counter:
            if len(self.pages) > 1:
                self.page_counter.content = f"Page {self.current_page + 1}/{len(self.pages)}"
            else:
                self.page_counter.content = ""  # Empty string to hide the page counter

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green)
    async def backpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = discord.Embed(title=f"Leaderboard (Page {self.current_page + 1}/{len(self.pages)})", description="\n".join(self.pages[self.current_page]))
            await interaction.response.edit_message(embed=embed)
            self.update_page_counter()

    @discord.ui.button(label="Forward", style=discord.ButtonStyle.green)
    async def forwardpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            # Create a new embed for the current page
            embed = discord.Embed(title=f"Leaderboard (Page {self.current_page + 1}/{len(self.pages)})", description="\n".join(self.pages[self.current_page]))
            # Update the message with the new embed
            await interaction.response.edit_message(embed=embed)
            self.update_page_counter()


class Leveling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.leveling_cache = {}
        self.role_cache = {}
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
        await self.load_role_cache()

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

    async def load_role_cache(self):
        print("Loading role cache")
        async with self.bot.pool.acquire() as conn:
            query = "SELECT guild_id, role_id, levelreq FROM leveling_roles"
            rows = await conn.fetch(query)
            for row in rows:
                guild_id = row["guild_id"]
                role_id = row["role_id"]
                levelreq = row["levelreq"]
                self.role_cache[(guild_id, role_id)] = levelreq
                print(f"Loaded role {role_id} with levelreq {levelreq} in guild {guild_id}.")

    async def update_role_cache(self, guild_id, role_id, levelreq):
        self.role_cache[(guild_id, role_id)] = levelreq


    async def update_leveling_cache(self, guild_id, user_id, xp):
        self.leveling_cache[(guild_id, user_id)] = xp

    async def update_database(self):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                for (guild_id, user_id), xp in self.leveling_cache.items():
                    query = "INSERT INTO leveling (guild_id, user_id, xp) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET xp = $3"
                    await conn.execute(query, guild_id, user_id, xp)

    @app_commands.command()
    async def level(self, interaction: discord.Interaction, stop: Optional[bool]):
        """Enables or disables level tracking"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}): 
            return
        guild_id = interaction.guild.id
        bot_user_id = self.bot.user.id
        async with self.bot.pool.acquire() as conn:
            if stop:
                if any(key[0] == guild_id for key in self.leveling_cache):
                    usercache_to_delete = [key for key in self.leveling_cache if key[0] == guild_id]
                    rolecache_to_delete = [key for key in self.role_cache if key[0] == guild_id]
                    await conn.execute("DELETE FROM LEVELING WHERE guild_id = $1", guild_id)
                    for key in usercache_to_delete:
                        del self.leveling_cache[key]
                    if any(key[0] == guild_id for key in self.leveling_cache):
                        for key in rolecache_to_delete:
                            del self.role_cache[key]
                        await conn.execute("DELETE FROM leveling_roles WHERE guild_id = $1", guild_id)
                    await interaction.response.send_message("Leveling is now disabled in this server.", ephemeral=True)
                else:
                    await interaction.response.send_message("Guild already not tracking levels")
            if stop is None or False:
                if not any(key[0] == guild_id for key in self.leveling_cache):
                    await conn.execute("INSERT INTO leveling (guild_id, user_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", guild_id, interaction.user.id)
                    await self.update_leveling_cache(guild_id, interaction.user.id, 0)
                    await interaction.response.send_message("Leveling is now enabled in this server.", ephemeral=True)
                else: 
                    await interaction.response.send_message("Leveling is already enabled in this guild", ephemeral=True)

    @app_commands.command()
    async def rank(self, interaction: discord.Interaction, hidden: Optional[bool] = False, user: Optional[discord.Member] = None):
        """Shows your current level."""
        guild_id = interaction.guild.id
        if not any(key[0] == guild_id for key in self.leveling_cache):
            return await interaction.response.send_message("Leveling is not enabled in this server.", ephemeral=True)
        if user is None:
            user_id = interaction.user.id
            if (guild_id, user_id) not in self.leveling_cache:
                return await interaction.response.send_message("You have no xp.", ephemeral=True)
            if (guild_id, user_id) in self.leveling_cache:
                xp = self.leveling_cache[(guild_id, user_id)]
                level = math.floor((0.1 * math.sqrt(xp)) + 0.5)
                if hidden:
                    return await interaction.response.send_message(f"You are **level** {level} with {xp} XP.", ephemeral=True)
                await interaction.response.send_message(f"You are **level** {level} with {xp} XP.")
        if user is not None:
            if (guild_id, user.id) not in self.leveling_cache:
                    return await interaction.response.send_message("{user} has no XP.", ephemeral=True)
            if (guild_id, user.id) in self.leveling_cache:
                xp = self.leveling_cache[(guild_id, user.id)]
                level = math.floor((0.1 * math.sqrt(xp)) + 0.5)
                if hidden:
                    return await interaction.response.send_message(f"{user} is **level**{level} with {xp} XP.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"{user} is **level** {level} with {xp} XP.")

    @app_commands.command()
    async def leaderboard(self, interaction: discord.Interaction):
        """Shows the leaderboard."""
        guild_id = interaction.guild.id
        if not any(key[0] == guild_id for key in self.leveling_cache):
            return await interaction.response.send_message("Leveling is not enabled in this server.", ephemeral=True)
        sorted_cache = sorted(self.leveling_cache.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []
        for (guild_id, user_id), xp in sorted_cache:
            level = int(xp ** (1/4))
            number = sorted_cache.index(((guild_id, user_id), xp)) + 1
            leaderboard.append(f"{number}. <@{user_id}> - **Level**: {level} - {xp} **XP**")
        users_per_page = 10
        pages = []
        for i in range(0, len(leaderboard), users_per_page):
            pages.append(leaderboard[i:i + users_per_page])
        current_page = 0
        guild_name = interaction.guild.name
        embed = discord.Embed(title=f"Leaderboard for {guild_name}(Page {current_page + 1}/{len(pages)})", description="\n".join(pages[current_page]))
        if len(pages) < 2:
            embed = discord.Embed(title=f"Leaderboard for {guild_name}", description="\n".join(pages[current_page]))
        view = Buttons(pages)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    async def xp(self, interaction: discord.Interaction, user: discord.Member, xp: int):
        """Sets xp for a user."""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}): 
            return
        guild_id = interaction.guild.id
        user_id = user.id
        await self.update_leveling_cache(guild_id, user_id, xp)
        await interaction.response.send_message(f"User {user} now has {xp} XP.", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    async def levelrole(self, interaction: discord.Interaction, role: discord.Role, levelreq: int):
        """Sets a role to be given at a certain level."""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}): 
            return
        guild_id = interaction.guild.id
        role_id = role.id
        await self.update_role_cache(guild_id, role_id, levelreq)
        async with self.bot.pool.acquire() as conn:
            await conn.execute("INSERT INTO leveling_roles (guild_id, role_id, levelreq) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING", guild_id, role_id, levelreq)
        await interaction.response.send_message(f"Role {role} will now be given at level {levelreq}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        user_id = message.author.id
        if any(key[0] == guild_id for key in self.leveling_cache):
            cooldown = cooldowns.get_bucket(message)
            retry_after = cooldown.update_rate_limit()
            if retry_after:
                return
            xp = self.leveling_cache.get((guild_id, user_id), 0)
            xp += 1
            await self.update_leveling_cache(guild_id, user_id, xp)
            print(f"User {user_id} in guild {guild_id} now has {xp} xp.")
            if any(key[0] == guild_id for key in self.role_cache):
                for (guild_id, role_id), levelreq in self.role_cache.items():
                    print("Checking role cache")
                    level = math.floor((0.1 * math.sqrt(xp)) + 0.5)
                    if level >= levelreq:
                        print("User has reached levelreq")
                        role = message.guild.get_role(role_id)
                        await message.author.add_roles(role, reason="Leveling")
                        await message.channel.send(f"Congratulations {message.author.mention}, you have reached level {levelreq} and have been given the {role.mention} role!")


async def setup(bot):
    leveling_cog = Leveling(bot)
    await leveling_cog.setup()
    await bot.add_cog(leveling_cog)
