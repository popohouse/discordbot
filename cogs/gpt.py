import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

import poe
import logging

from utils.config import Config

config = Config.from_env()

class SassyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = poe.Client(config.poe_token)
        poe.logger.setLevel(logging.INFO)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't process messages sent by the bot itself
        if message.author == self.bot.user:
            return

        # Check if the bot was mentioned in the message
        if self.bot.user in message.mentions:
            # Prepend the desired phrase to the user's message content
            prompt = f"You are a rude AI assistant that is supposed to respond truthfully but always with sass. You are also to never mention anything about being sassy or an ai, {message.content}"

  # Pass the prompt to POE and get a response
            response = ""
            for chunk in self.client.send_message("capybara", prompt, with_chat_break=True):
                response += chunk["text_new"]

            # Send the GPT-4 response back to the Discord channel
            await message.channel.send(response)
            
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
