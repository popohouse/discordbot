import discord
from discord.ext import commands
import aiohttp
import os

class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def cat(self, ctx, *, subcommand=None):
        if subcommand is None:
            url = 'https://cataas.com/cat'
        else:
            url = f'https://cataas.com/cat/{subcommand}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not get cat image :(')
                data = await resp.read()
                content_type = resp.headers['Content-Type']
                extension = content_type.split('/')[-1]
                filename = f'cat.{extension}'
                with open(filename,'wb') as f:
                    f.write(data)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)
        
async def setup(bot):
    await bot.add_cog(CatCog(bot))
