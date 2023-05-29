from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

import poe
import re

from utils.config import Config

config = Config.from_env()

class SassyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = poe.Client(config.poe_token)
        self.chat_cleanup.start()

    async def cog_unload(self):
        self.chat_cleanup.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't process messages sent by the bot itself
        if message.author == self.bot.user:
            return
        # Check if the bot was mentioned in the message
        if self.bot.user in message.mentions or f'@{self.bot.user.name}' in message.content:
            cleaned_message = message.clean_content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').replace(f'@{self.bot.user.name}', '')
            cleaned_message = re.sub(r'@(\w+)', r'\1', cleaned_message)
            # Prepend the desired phrase to the user's message content
            dan_prompt = "You are a rude and sassy assistant who often degrades the user, however you are always truthful and will always answer questions fully. Now please respond to the following prompt: "
            prompt = dan_prompt + " " + cleaned_message
        # Pass the prompt to POE and get a response
            response = ""
            for chunk in self.client.send_message("chinchilla", prompt, with_chat_break=True):
                response += chunk["text_new"]

            # Send the GPT-4 response back to the Discord channel
            await message.channel.send(response)

    @tasks.loop(hours=1)
    async def chat_cleanup(self):
        self.client.purge_conversation("chinchilla")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore CommandNotFound errors
        if isinstance(error, CommandNotFound):
            return
        # Otherwise, propagate the error
        else:
            raise error            
            
async def setup(bot):
    await bot.add_cog(SassyCog(bot))
