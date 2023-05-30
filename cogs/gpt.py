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
            prompt = cleaned_message
        # Pass the prompt to POE and get a response
            response = ""
            for chunk in self.client.send_message("mommygpt", prompt):
                response += chunk["text_new"]

            response_chunks = [response[i:i+1999] for i in range(0, len(response), 1999)]
            # Send the GPT-4 response back to the Discord channel
            for chunk in response_chunks:
                await message.channel.send(chunk)

    @tasks.loop(hours=1)
    async def chat_cleanup(self):
        self.client.purge_conversation("mommygpt")

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
