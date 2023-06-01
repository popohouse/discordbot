from discord.ext import commands
import re
from discord import app_commands
import discord
from typing import Optional
import json
from utils import permissions

###Possible todo###
#Implement limit of AR per guild in both database and cache
#Possibly add timestamp to AR when triggered so can cleanup old ones
#Add cooldown to AR
#Add ability to add AR to specific channel(s)/ignore specific channel(s)
#Add ability to add AR to specific role(s)/ignore specific role(s)
#Ignore bots
#Ingore certain roles
#Allow users to edit response
#Dont display buttons if only one page, only don't display the Page x/y part
class Buttons(discord.ui.View):
    def __init__(self, pages):
        super().__init__()
        self.value = None
        self.pages = pages
        self.current_page = 0
        self.page_counter = None

    def update_page_counter(self):
        if self.page_counter:
            self.page_counter.content = f"Page {self.current_page + 1}/{len(self.pages)}"

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
        async with self.bot.pool.acquire() as conn:
            await self.update_cache()

    async def update_cache(self, guild_id=None):
        try:
            if guild_id is not None and guild_id in self.auto_responses_cache:
                del self.auto_responses_cache[guild_id]  # Clear existing cache for the guild
            async with self.bot.pool.acquire() as conn:
                if guild_id is None:
                    auto_responses = await conn.fetch(
                        "SELECT guild_id, triggers, response, ping FROM auto_responses"
                    )
                else:
                    auto_responses = await conn.fetch(
                        "SELECT guild_id, triggers, response, ping FROM auto_responses WHERE guild_id = $1",
                        guild_id
                    )
                for row in auto_responses:
                    guild_id = row["guild_id"]
                    triggers = row["triggers"]
                    response = row["response"]
                    ping = row["ping"]
                    if guild_id not in self.auto_responses_cache:
                        self.auto_responses_cache[guild_id] = []
                    self.auto_responses_cache[guild_id].append(
                        {"triggers": triggers, "response": response, "ping": ping}
                    )
        except Exception as e:
            print(f"Failed to fetch auto responses: {str(e)}")

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def addar(self, interaction: discord.Interaction, trigger: str, response: str, ping: Optional[bool] = False):
        """Add auto response"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Try to parse the response string as a JSON object
            response_data = json.loads(response)
            # Check if the JSON object has an "embeds" key
            if "embeds" in response_data:
                # The response is a valid JSON object representing an embed, store it as-is
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
                await conn.execute("INSERT INTO auto_responses (guild_id, triggers, response, ping) VALUES ($1, $2, $3, $4)", interaction.guild.id, [trigger], json.dumps(response_data), ping)
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
                auto_response = await conn.fetchrow(
                    "SELECT guild_id FROM auto_responses WHERE id = $1", id
                )
                if auto_response and auto_response["guild_id"] == interaction.guild.id:
                    # Add the alias to the triggers array for the specified auto response
                    await conn.execute(
                        "UPDATE auto_responses SET triggers = array_append(triggers, $3) WHERE guild_id = $1 AND id = $2",
                        interaction.guild.id, id, alias
                    )
                    await self.update_cache(interaction.guild.id)
                    await interaction.response.send_message("Alias added successfully!", ephemeral=True)
                else:
                    await interaction.response.send_message("Unknown autoresponse.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def removear(self, interaction: discord.Interaction, id: int, alias: Optional[str]):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Check if the guild owns the autoresponse
            async with self.bot.pool.acquire() as conn:
                auto_response = await conn.fetchrow(
                    "SELECT guild_id FROM auto_responses WHERE id = $1", id
                )
                if auto_response and auto_response["guild_id"] == interaction.guild.id:
                    # Remove the alias from the triggers array for the specified auto response
                    if alias is not None:
                        await conn.execute(
                            "UPDATE auto_responses SET triggers = array_remove(triggers, $3) WHERE guild_id = $1 AND id = $2",
                            interaction.guild.id, id, alias
                        )
                        await self.update_cache(interaction.guild.id)
                        await interaction.response.send_message("Alias removed successfully!", ephemeral=True)
                    else:
                        await conn.execute(
                            "DELETE FROM auto_responses WHERE guild_id = $1 AND id = $2",
                            interaction.guild.id, id
                        )
                        await self.update_cache(interaction.guild.id)
                        await interaction.response.send_message("Response removed successfully!", ephemeral=True)
                else:
                    await interaction.response.send_message("Unknown autoresponse.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def listresponses(self, interaction: discord.Interaction):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Retrieve auto responses from the database
            async with self.bot.pool.acquire() as conn:
                auto_responses = await conn.fetch(
                    "SELECT id, triggers, response FROM auto_responses WHERE guild_id = $1", interaction.guild.id
                )
                # Format the auto responses as a list of strings (pages)
                pages = []
                page_limit = 2000  # Character limit per page
                response_str = "Auto responses:\n"
                for row in auto_responses:
                    entry = f"ID: {row['id']}\nTriggers: {', '.join(row['triggers'])}\nResponse: {row['response']}\n\n"
                    if len(response_str) + len(entry) > page_limit:
                        pages.append(response_str)
                        response_str = ""
                    response_str += entry
                pages.append(response_str)
            view = Buttons(pages)
            view.page_counter = await interaction.response.send_message(
                f"{pages[0]}Page 1/{len(pages)}", view=view, ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"Failed to list auto responses: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            guild_id = message.guild.id
            if guild_id in self.auto_responses_cache:
                auto_responses = self.auto_responses_cache[guild_id]
                for response_data in auto_responses:
                    for trigger in response_data["triggers"]:
                        if re.search(trigger, message.content):
                            response = response_data["response"]
                            ping = response_data["ping"]
                            try:
                                response_data = json.loads(response)
                                if isinstance(response_data, dict) and "embeds" in response_data:
                                    for embed in response_data["embeds"]:
                                        if ping:
                                            await message.channel.send(
                                                f"{message.author.mention}",
                                                embed=discord.Embed.from_dict(embed),
                                            )
                                        else:
                                            await message.channel.send(
                                                embed=discord.Embed.from_dict(embed)
                                            )
                                else:
                                    raise json.JSONDecodeError("", "", 0)
                            except json.JSONDecodeError:
                                escaped_response = response.replace("{", "{{").replace(
                                    "}", "}}"
                                ).strip('"')
                                if ping:
                                    await message.channel.send(
                                        f"{message.author.mention} {escaped_response}"
                                    )
                                else:
                                    await message.channel.send(escaped_response)
                            break


async def setup(bot):
    autoresponsecog_cog = AutoResponseCog(bot)
    await autoresponsecog_cog.setup()
    await bot.add_cog(autoresponsecog_cog)