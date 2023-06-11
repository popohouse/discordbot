from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
import discord
import poe
from typing import Optional
from utils.config import Config
from discord import app_commands

config = Config.from_env()


class SassyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = poe.Client(config.poe_token)
        #self.chat_cleanup.start()

    #async def cog_unload(self):
        #self.chat_cleanup.cancel()

    @app_commands.command()
    @app_commands.choices(model=[
        app_commands.Choice(name="Claude", value="a2"),
        app_commands.Choice(name="ChatGPT", value="chinchilla"),
        app_commands.Choice(name="UwUbot", value="uwuify"),
    ])
    async def gpt(self, interaction: discord.Interaction, prompt: str, model: Optional[app_commands.Choice[str]] = 'ChatGpt'):
        # Check if the bot was mentioned in the message
            # Prepend the desired phrase to the user's message content
        # Pass the prompt to POE and get a response
            try:
                model_name = model.name
                if model_name is None:
                    model_name = 'ChatGPT'
                print (interaction.user.name, prompt, model_name)
                models = {
                'Claude': 'a2',
                'ChatGPT': 'chinchilla',
                'UwUbot': 'uwuify'
                        }
                base = f'*model*: `{model_name}`\n'
                token = config.poe_token
                client = poe.Client(token)
                await interaction.response.send_message(base)
                base += '\n'
                completion = client.send_message(models[model_name], prompt, with_chat_break=True)
                for token in completion:
                    base += token['text_new']
                    base = base.replace('Discord Message:', '')
                    await interaction.edit_original_response(content=base)
            except Exception as e:
                print (e)

    #Cleanup of old chat messages, possibly do this another way.
    #@tasks.loop(hours=1)
    #async def chat_cleanup(self):
    #    self.client.purge_conversation("uwuify")
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore CommandNotFound errors
        if isinstance(error, CommandNotFound):
            return
        # Otherwise, propagate the error
        raise error


async def setup(bot):
    await bot.add_cog(SassyCog(bot))