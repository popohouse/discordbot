from discord.ext import commands
import re
from discord import app_commands
import discord
from typing import Optional, List
import json
from utils import permissions

cooldowns = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.user)


class Buttons(discord.ui.View):
    def __init__(self, pages):
        super().__init__()
        self.value = None
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
            await interaction.response.edit_message(content=f"{self.pages[self.current_page]}Page {self.current_page + 1}/{len(self.pages)}")
            self.update_page_counter()

    @discord.ui.button(label="Forward", style=discord.ButtonStyle.green)
    async def forwardpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(content=f"{self.pages[self.current_page]}Page {self.current_page + 1}/{len(self.pages)}")
            self.update_page_counter()



class AutoResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_responses_cache = {}

    async def setup(self):
        await self.update_cache()

    async def update_cache(self, guild_id=None):
        try:
            if guild_id is not None and guild_id in self.auto_responses_cache:
                del self.auto_responses_cache[guild_id]  # Clear existing cache for the guild
            async with self.bot.pool.acquire() as conn:
                if guild_id is None:
                    auto_responses = await conn.fetch("SELECT guild_id, triggers, deletemsg, ignoreroles, selfdelete FROM auto_responses")
                else:
                    auto_responses = await conn.fetch("SELECT guild_id, triggers, deletemsg, ignoreroles, selfdelete FROM auto_responses WHERE guild_id = $1", guild_id)
                for row in auto_responses:
                    guild_id = row["guild_id"]
                    triggers = row["triggers"]
                    deletemsg = row["deletemsg"]
                    ignoreroles = row["ignoreroles"]
                    selfdelete = row["selfdelete"]
                    if guild_id not in self.auto_responses_cache:
                        self.auto_responses_cache[guild_id] = []
                    self.auto_responses_cache[guild_id].append({"triggers": triggers, "deletemsg": deletemsg, "ignoreroles": ignoreroles, "selfdelete": selfdelete})
        except Exception as e:
            print(f"Failed to fetch auto responses: {str(e)}")

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def addar(self, interaction: discord.Interaction, trigger: str, response: str, ping: Optional[bool] = False, deletemsg: Optional[bool] = False, selfdelete: Optional[int] = None, ignoreroles: Optional[discord.Role] = None):
        """Add auto response"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        if selfdelete is not None and selfdelete > 600:
            await interaction.response.send_message("Self delete time cannot be greater than 10 minutes.", ephemeral=True)
            return
        if ping and selfdelete < 180:
            await interaction.response.send_message("Self delete time must be at least 3 minutes if pinging.", ephemeral=True)
            return
        async with self.bot.pool.acquire() as conn: 
            total_ars = await conn.fetchval("SELECT COUNT(*) FROM auto_responses WHERE guild_id = $1", interaction.guild.id)
        if total_ars >= 20:
            await interaction.response.send_message("You can only have up to 20 auto responses.", ephemeral=True)
            return
        try:
            response_data = json.loads(response)
            # Check if the JSON object has an "embeds" key
            if "embeds" in response_data:
                pass
            else:
                # The response is not a valid JSON object representing an embed, raise an error to fall back to storing it as a regular string
                raise json.JSONDecodeError("", "", 0)
        except json.JSONDecodeError:
            # The response is not a valid JSON object, store it as a regular string
            response_data = response
        try:
            # Split the triggers string into a list of individual triggers
            trigger = re.sub(r'^/(.*)/[^/]*$', r'\1', trigger)
            # Store the triggers and response in the database
            async with self.bot.pool.acquire() as conn:
                await conn.execute("INSERT INTO auto_responses (guild_id, triggers, response, ping, deletemsg, selfdelete, ignoreroles) VALUES ($1, $2, $3, $4, $5, $6, $7)", interaction.guild.id, [trigger], json.dumps(response_data), ping, deletemsg, selfdelete if selfdelete else None, [ignoreroles.id] if ignoreroles else None)
                await self.update_cache(interaction.guild.id)
                await interaction.response.send_message("Auto response added successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add auto response: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def addaralias(self, interaction: discord.Interaction, id: int, alias: str):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Check if the guild owns the autoresponse
            async with self.bot.pool.acquire() as conn:
                auto_response = await conn.fetchrow("SELECT guild_id FROM auto_responses WHERE id = $1", id)
                if auto_response and auto_response["guild_id"] == interaction.guild.id:
                    # Add the alias to the triggers array for the specified auto response
                    await conn.execute("UPDATE auto_responses SET triggers = array_append(triggers, $3) WHERE guild_id = $1 AND id = $2", interaction.guild.id, id, alias)
                    await self.update_cache(interaction.guild.id)
                    await interaction.response.send_message("Alias added successfully!", ephemeral=True)
                else:
                    await interaction.response.send_message("Unknown autoresponse.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def delar(self, interaction: discord.Interaction, id: int, alias: Optional[str]):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Check if the guild owns the autoresponse
            async with self.bot.pool.acquire() as conn:
                auto_response = await conn.fetchrow(
                    "SELECT guild_id FROM auto_responses WHERE id = $1", id)
                if auto_response and auto_response["guild_id"] == interaction.guild.id:
                    # Remove the alias from the triggers array for the specified auto response
                    if alias is not None:
                        await conn.execute("UPDATE auto_responses SET triggers = array_remove(triggers, $3) WHERE guild_id = $1 AND id = $2", interaction.guild.id, id, alias)
                        await self.update_cache(interaction.guild.id)
                        await interaction.response.send_message("Alias removed successfully!", ephemeral=True)
                    else:
                        await conn.execute("DELETE FROM auto_responses WHERE guild_id = $1 AND id = $2", interaction.guild.id, id)
                        await self.update_cache(interaction.guild.id)
                        await interaction.response.send_message("Response removed successfully!", ephemeral=True)
                else:
                    await interaction.response.send_message("Unknown autoresponse.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def listar(self, interaction: discord.Interaction):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                auto_responses = await conn.fetch("SELECT id, triggers, response, ping, deletemsg FROM auto_responses WHERE guild_id = $1", interaction.guild.id)
            if not auto_responses:
                await interaction.response.send_message("No auto responses found.", ephemeral=True)
                return
            pages = []
            page_limit = 2000  # Character limit per page
            response_str = "Auto responses:\n"
            for row in auto_responses:
                entry = f"ID: {row['id']}\n**Triggers**: {', '.join(row['triggers'])}\n**Response**: {row['response']}\n **Ping**: {row['ping']} **Delete message**: {row['deletemsg']}\n\n"
                if len(response_str) + len(entry) > page_limit:
                    pages.append(response_str)
                    response_str = ""
                response_str += entry
            if response_str:  # Add any remaining entries to the last page
                pages.append(response_str)
            if len(pages) == 1:  # If there is only one page, send without page counter
                await interaction.response.send_message(pages[0], ephemeral=True)
            else:
                view = Buttons(pages)
                view.page_counter = await interaction.response.send_message(f"{pages[0]}Page 1/{len(pages)}", view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to list auto responses: {str(e)}", ephemeral=True)


    def should_ignore_message(self, message, ignoreroles):
        if ignoreroles:
            member = message.author
            guild = message.guild
            guild_roles = guild.roles
            ignored_role_objects = [discord.utils.get(guild_roles, id=role_id) for role_id in ignoreroles]
            return any(role in member.roles for role in ignored_role_objects)
        return False

    async def send_response(self, message, response, ping, deletemsg, selfdelete):
        if ping:
            content = f"{message.author.mention} {response}"
        else:
            content = response
        if deletemsg:
            await message.delete()
        response_message = await message.channel.send(content)
        if selfdelete:
            await response_message.delete(delay=selfdelete)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            guild_id = message.guild.id
            if guild_id in self.auto_responses_cache:
                auto_responses = self.auto_responses_cache[guild_id]
                for response_data in auto_responses:
                    for trigger in response_data["triggers"]:
                        if re.search(trigger, message.content):
                            trigger_data = response_data
                            triggers = trigger_data["triggers"]
                            deletemsg = trigger_data["deletemsg"]
                            ignoreroles = trigger_data["ignoreroles"]
                            selfdelete = trigger_data["selfdelete"]
                            if self.should_ignore_message(message, ignoreroles):
                                return
                            cooldown = cooldowns.get_bucket(message)
                            retry_after = cooldown.update_rate_limit()
                            if retry_after:
                                if deletemsg:
                                    await message.delete()
                                return
                            async with self.bot.pool.acquire() as conn:
                                auto_response = await conn.fetchrow(
                                    "SELECT response, ping FROM auto_responses WHERE triggers = $1",
                                    triggers
                                )
                            if auto_response:
                                response = auto_response["response"]
                                ping = auto_response["ping"]
                                try:
                                    response_data = json.loads(response)
                                    if isinstance(response_data, dict) and "embeds" in response_data:
                                        for embed in response_data["embeds"]:
                                            await self.send_response(message, discord.Embed.from_dict(embed), ping, deletemsg, selfdelete)
                                    else:
                                        raise json.JSONDecodeError("", "", 0)
                                except json.JSONDecodeError:
                                    escaped_response = response.replace("{", "{{").replace("}", "}}").strip('"')
                                    await self.send_response(message, escaped_response, ping, deletemsg, selfdelete)
                                return



async def setup(bot):
    autoresponsecog_cog = AutoResponseCog(bot)
    await autoresponsecog_cog.setup()
    await bot.add_cog(autoresponsecog_cog)