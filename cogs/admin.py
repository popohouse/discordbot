import discord
from discord import app_commands
from discord.ext import commands
import importlib
import os
from utils import default
from utils import config

config = config.Config.from_env(".env")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def amiadmin(self, interaction: discord.Interaction):
        """Are you an admin?"""
        if interaction.user.id == config.discord_owner_id:
            return await interaction.response.send_message(f"Yes **{interaction.user.name}** you are an admin! ✅", ephemeral=True)
        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        if interaction.user.id == 86477779717066752:
            return await interaction.response.send_message(f"Well kinda **{interaction.user.name}**.. you still own the source code", ephemeral=True)
        await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def load(self, interaction: discord.Interaction, name: str):
        """Loads an extension."""
        if interaction.user.id == config.discord_owner_id:
            try:
                await self.bot.load_extension(f"cogs.{name}")
            except Exception as e:
                return await interaction.response.send_message(default.traceback_maker(e))
            await interaction.response.send_message(f"Loaded extension **{name}.py**", ephemeral=True)
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def unload(self, interaction: discord.Interaction, name: str):
        """Unloads an extension."""
        if interaction.user.id == config.discord_owner_id:
            try:
                await self.bot.unload_extension(f"cogs.{name}")
            except Exception as e:
                return await interaction.response.send_message(default.traceback_maker(e))
            await interaction.response.send_message(f"Unloaded extension **{name}.py**", ephemeral=True)
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def reload(self, interaction: discord.Interaction, name: str):
        """Reloads an extension."""
        if interaction.user.id == config.discord_owner_id:
            try:
                await self.bot.reload_extension(f"cogs.{name}")
                await interaction.response.send_message(f"Reloaded extension **{name}.py**", ephemeral=True)
            except Exception as e:
                return await interaction.response.send_message(default.traceback_maker(e))
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def reloadall(self, interaction: discord.Interaction):
        """Reloads all extensions."""
        if interaction.user.id == config.discord_owner_id:
            error_collection = []
            for file in os.listdir("cogs"):
                if not file.endswith(".py"):
                    continue

                name = file[:-3]
                try:
                    await self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

            if error_collection:
                output = "\n".join([
                    f"**{g[0]}** ```diff\n- {g[1]}```"
                    for g in error_collection
                ])

                return await interaction.response.send_message(
                    f"Attempted to reload all extensions, was able to reload, "
                    f"however the following failed...\n\n{output}", ephemeral=True
                )

            await interaction.response.send_message("Successfully reloaded all extensions", ephemeral=True)
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def reloadutils(self, interaction: discord.Interaction, name: str):
        """Reloads a utils module."""
        if interaction.user.id == config.discord_owner_id:
            name_maker = f"utils/{name}.py"
            try:
                module_name = importlib.import_module(f"utils.{name}")
                importlib.reload(module_name)
            except ModuleNotFoundError:
                return await interaction.response.send_message(f"Couldn't find module named **{name_maker}**", ephemeral=True)
            except Exception as e:
                error = default.traceback_maker(e)
                return await interaction.response.send_message(f"Module **{name_maker}** returned error and was not reloaded...\n{error}", ephemeral=True)
            await interaction.response.send_message(f"Reloaded module **{name_maker}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)

    @app_commands.command()
    async def dm(self, interaction: discord.Interaction, user: discord.User, *, message: str):
        """DM the user of your choice"""
        if interaction.user.id == config.discord_owner_id:
            try:
                await user.send(message)
                await interaction.response.send_message(f"✉️ Sent a DM to **{user}**", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("This user might be having DMs blocked or it's a bot account...", ephemeral=True)
        else:
            await interaction.response.send_message(f"no, heck off {interaction.user.name}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))