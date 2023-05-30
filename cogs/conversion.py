
import discord
from discord import app_commands
from discord.ext import commands
from pint import UnitRegistry
from typing import Optional

class ConversionCog(commands.Cog):
    def __init__(self, bot: commands.Bot)-> None:
        self.bot = bot
        self.ureg = UnitRegistry()
        
    @app_commands.command()
    async def convert(self, interaction: discord.Interaction, value: Optional[float] = None, from_unit: Optional[str]  = None, to_unit: Optional[str] = None)-> None:
        """Convert between common units"""
        if value and from_unit and to_unit:
            try:
                quantity = self.ureg.Quantity(value, self.ureg(from_unit))
                
                # temperature conversion
                if from_unit in ['degC', 'degF', 'kelvin'] and to_unit in ['degC', 'degF', 'kelvin']:
                    quantity.ito(self.ureg(to_unit))
                
                # other conversions
                else:
                    quantity = quantity.to(self.ureg(to_unit))
                
                await interaction.response.send_message(f"{value} {from_unit} is {quantity.magnitude:.2f} {to_unit}")
            except Exception as e:
                await interaction.response.send_message(f"Error during conversion: {str(e)}")
        else:
            await interaction.response.send_message("Please provide a value, a from_unit, and a to_unit")


async def setup(bot):
    await bot.add_cog(ConversionCog(bot))         