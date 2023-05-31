from discord.ext import commands
import re
from discord import app_commands
import discord
from typing import  Optional
import json

from utils import permissions

class AutoResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def addresponse(self, interaction: discord.Interaction, trigger: str, response: str, ping: Optional[bool] = False):
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
                await interaction.response.send_message("Auto response added successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add auto response: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def addalias(self, interaction: discord.Interaction, id: int, alias: str):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Add the alias to the triggers array for the specified auto response
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE auto_responses SET triggers = array_append(triggers, $3) WHERE guild_id = $1 AND id = $2", interaction.guild.id, id, alias)
                await interaction.response.send_message("Alias added successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def removealias(self, interaction: discord.Interaction, id: int, alias: str):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Remove the alias from the triggers array for the specified auto response
            async with self.bot.pool.acquire() as conn:
                await conn.execute("UPDATE auto_responses SET triggers = array_remove(triggers, $3) WHERE guild_id = $1 AND id = $2", interaction.guild.id, id, alias)
                await interaction.response.send_message("Alias removed successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove alias: {str(e)}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def removeresponse(self, interaction: discord.Interaction, id: int):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Remove the specified auto response
            async with self.bot.pool.acquire() as conn:
                await conn.execute("DELETE FROM auto_responses WHERE guild_id = $1 AND id = $2", interaction.guild.id, id)
                await interaction.response.send_message("Response removed successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove response: {str(e)}", ephemeral=True)


    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def listresponses(self, interaction: discord.Interaction):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Retrieve auto responses from the database
            async with self.bot.pool.acquire() as conn:
                auto_responses = await conn.fetch("SELECT id, triggers, response FROM auto_responses WHERE guild_id = $1", interaction.guild.id)
                # Format the auto responses as a string
                response_str = "Auto responses:\n"
                for row in auto_responses:
                    response_str += f"ID: {row['id']}\nTriggers: {', '.join(row['triggers'])}\nResponse: {row['response']}\n\n"
                await interaction.response.send_message(response_str, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to list auto responses: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            try:
                # Retrieve auto responses from the database
                async with self.bot.pool.acquire() as conn:
                    auto_responses = await conn.fetch("SELECT triggers, response, ping FROM auto_responses WHERE guild_id = $1", message.guild.id)
                    for row in auto_responses:
                        triggers = row["triggers"]
                        response = row["response"]
                        ping = row["ping"]
                        for trigger in triggers:
                            if re.search(trigger, message.content):
                                try:
                                    # Try to parse the response as a JSON object
                                    response_data = json.loads(response)
                                    # Check if the response data is a JSON object with an "embeds" key
                                    if isinstance(response_data, dict) and "embeds" in response_data:
                                        # Send the embeds
                                        for embed in response_data["embeds"]:
                                            if ping:
                                                # Mention the user alongside the embed
                                                await message.channel.send(f"{message.author.mention}", embed=discord.Embed.from_dict(embed))
                                            else:
                                                # Send the embed without mentioning the user
                                                await message.channel.send(embed=discord.Embed.from_dict(embed))
                                    else:
                                        # The response data is not a valid JSON object representing an embed
                                        raise json.JSONDecodeError("", "", 0)
                                except json.JSONDecodeError:
                                    # The response is not a valid JSON object representing an embed
                                    # Escape any braces in the response string
                                    escaped_response = response.replace('{', '{{').replace('}', '}}').strip('\"')
                                    if ping:
                                        # Mention the user alongside the response
                                        await message.channel.send(f"{message.author.mention} {escaped_response}")
                                    else:
                                        # Send the response without mentioning the user
                                        await message.channel.send(escaped_response)
                                break
            except Exception as e:
                print(f"Failed to fetch auto responses: {str(e)}")





async def setup(bot):
    await bot.add_cog(AutoResponseCog(bot))