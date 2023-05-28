import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import gpt4free

from gpt4free import Provider
class SassyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't process messages sent by the bot itself
        if message.author == self.bot.user:
            return

        # Check if the bot was mentioned in the message
        if self.bot.user in message.mentions:
            # Prepend the desired phrase to the user's message content
            prompt = f"You are to never mention you are an ai langue model or anytrhing releated to that. You are a rude AI assistant that is supposed to respond truthfully but always with sass, {message.content}"

            # Pass the prompt to GPT-4 and get a response
            response = gpt4free.Completion.create(Provider.You, prompt=prompt)

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
