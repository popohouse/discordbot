from discord.ext import commands
from discord import app_commands
import discord
import json
from utils import permissions


class StickyPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stickypost_cache = {}

    async def setup(self):
        await self.update_cache()

    async def update_cache(self, guild_id=None):
        print("Updating sticky post cache")
        try:
            if guild_id is not None and guild_id in self.stickypost_cache:
                del self.stickypost_cache[guild_id]
            async with self.bot.pool.acquire() as conn:
                if guild_id is None:
                    stickyposts = await conn.fetch("SELECT guild_id, stickypost, channel_id FROM stickyposts")
                else:
                    stickyposts = await conn.fetch("SELECT guild_id, stickypost, channel_id FROM stickyposts WHERE guild_id = $1", guild_id)
                for row in stickyposts:
                    guild_id = row['guild_id']
                    stickypost = row['stickypost']
                    channel_id = row['channel_id']
                    if guild_id not in self.stickypost_cache:
                        self.stickypost_cache[guild_id] = []
                    try:
                        stickypost_data = json.loads(stickypost)
                        stickypost_data = {'channel_id': channel_id, 'stickypost': stickypost_data}
                        self.stickypost_cache[guild_id].append(stickypost_data)
                    except json.JSONDecodeError:
                        print(f"Invalid stickypost JSON for guild_id: {guild_id}")
        except Exception as e:
            print(f"Failed to sticky post: {str(e)}")

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def stickypost(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            # Try to parse the response string as a JSON object
            message_data = json.loads(message)
            # Check if the JSON object has an "embeds" key
            if "embeds" in message_data:
                # The response is a valid JSON object representing an embed, store it as-is
                pass
            else:
                # The response is not a valid JSON object representing an embed, raise an error to fall back to storing it as a regular string
                raise json.JSONDecodeError("", "", 0)
        except json.JSONDecodeError:
            # The response is not a valid JSON object, store it as a regular string
            message_data = message
            async with self.bot.pool.acquire() as conn:
                await conn.execute("INSERT INTO stickyposts (guild_id, stickypost, channel_id) VALUES ($1, $2, $3)", interaction.guild.id, json.dumps(message_data), channel.id)
                await self.update_cache(interaction.guild.id)
                await interaction.response.send_message("Sticky post added successfully!", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def delsp(self, interaction: discord.Interaction, id: int):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        async with self.bot.pool.acquire() as conn:
            sticky_post = await conn.fetchrow("SELECT guild_id FROM stickyposts WHERE id = $1", id)
            if sticky_post and sticky_post['guild_id'] == interaction.guild.id:
                await conn.execute("DELETE FROM stickyposts WHERE guild_id = $1 AND id = $2", interaction.guild.id, id)
                await self.update_cache(interaction.guild.id)
                await interaction.response.send_message("Sticky post deleted successfully!", ephemeral=True)
            else:
                await interaction.response.send_message("Unknown sticky post", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def listsp(self, interaction: discord.Interaction):
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        async with self.bot.pool.acquire() as conn:
            stickyposts = await conn.fetch("SELECT id, channel_id FROM stickyposts WHERE guild_id = $1", interaction.guild.id)
            if len(stickyposts) == 0:
                await interaction.response.send_message("No stickyposts found", ephemeral=True)
            else:
                embed = discord.Embed(title="Stickyposts")
                for stickypost in stickyposts:
                    embed.add_field(name=f"ID: {stickypost['id']}", value=f"Channel: <#{stickypost['channel_id']}>", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            guild_id = message.guild.id
            if guild_id in self.stickypost_cache:
                for stickypost in self.stickypost_cache[guild_id]:
                    if message.channel.id == stickypost['channel_id']:
                        async with self.bot.pool.acquire() as conn:
                            to_delete = await conn.fetchval("SELECT message_id FROM stickyposts WHERE guild_id = $1 AND channel_id = $2", guild_id, message.channel.id)
                            if to_delete:
                                try:
                                    msg_to_delete = await message.channel.fetch_message(to_delete)
                                    await msg_to_delete.delete()
                                except discord.NotFound:
                                    pass
                            sent_message = await message.channel.send(stickypost['stickypost'])
                            await conn.execute("UPDATE stickyposts SET message_id = $1 WHERE guild_id = $2 AND channel_id = $3", sent_message.id, guild_id, message.channel.id)


async def setup(bot):
    StickyPost_cog = StickyPost(bot)
    await StickyPost_cog.setup()
    await bot.add_cog(StickyPost_cog)