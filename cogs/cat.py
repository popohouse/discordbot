import aiohttp

from discord.ext import commands


class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None

    @commands.command()
    async def cat(self, ctx):
        """ Post random cat image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                cat = await response.json()
                await ctx.send(cat[0]['url'])

async def setup(bot):
    await bot.add_cog(CatCog(bot))