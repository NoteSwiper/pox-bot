from typing import Optional
from discord.ext import commands
import discord
from discord import app_commands

from stuff import clamp

class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    calc_group = app_commands.Group(name="calculate", description="A group for calculator cogs")
    
    @calc_group.command(name="percentage")
    async def calculate_percentage(self, interaction: discord.Interaction, value: int, max: Optional[int]):
        if max is None:
            max = 100
        
        value = clamp(value,0,max)
        
        await interaction.response.send_message(f"Percentage: {round((value/max)*1000)/10}%! ;3")

async def setup(bot):
    await bot.add_cog(Calculator(bot))