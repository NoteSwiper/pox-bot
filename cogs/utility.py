from discord.ext import commands
from discord import app_commands, Interaction, Embed

from typing import Optional

import random
from bot import PoxBot
import data

from logger import logger

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    @app_commands.command(name="random_integer", description="Generates random integer.")
    @app_commands.describe(min="Minimum integer", max="Maximum integer")
    async def generate_integer(self, interaction: Interaction, min: Optional[int] = 0, max: Optional[int] = 10):
        if min is None:
            min = 0
        
        if max is None:
            max = 10
        
        e = Embed(title="Random number generator",description=f"Result is **{random.randint(min,max)}**.")

        await interaction.response.send_message(embed=e)
    
    
    @app_commands.command(name="random_float", description="Generates random float.")
    @app_commands.describe(min="Minimum float", max="Maximum float")
    async def generate_float(self, interaction: Interaction, min: Optional[float] = -1.0, max: Optional[float] = 1.0, ndigit: Optional[int] = 4):
        if min is None:
            min = -1.0
        
        if max is None:
            max = 1.0
        
        if ndigit is None:
            ndigit = 4
        
        result = round(random.uniform(min,max), ndigits=ndigit)
        
        e = Embed(title="Random number generator",description=f"Result is **{result}**.")

        await interaction.response.send_message(embed=e)

    @app_commands.command(name="8ball", description="Gives a random, classic magic 8-ball response to a user's question.")
    @app_commands.describe(question="Question to answer by 8ball.")
    async def eight_ball(self, interaction: Interaction, question: str):
        choice = random.choice(data.tyc)

        e = Embed(
            title=f"Question: `{question}`",
            description="",
        )

        e.description = f"Result: {choice}"

        await interaction.response.send_message(embed=e)
    
    @app_commands.command(name="coinflip", description="Flips a coin and says 'Heads' or 'Tails'.")
    @app_commands.describe(input="Text to desire.")
    async def coin_flip(self, interaction: Interaction, input: Optional[str] = None):
        result = "Heads." if random.randint(0, 1) == 1 else "Tails."

        e = Embed()

        if input is not None:
            e.title = f"`{input}`"
        
        e.description = f"Result: {result}"

        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Utility(bot))