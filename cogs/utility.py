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

    @app_commands.command(name="8ball", description="Gives a random, classic magic 8-ball response to a user's question.")
    @app_commands.describe(question="Question to answer by 8ball.")
    async def eight_ball(self, interaction: Interaction, question: str):
        choice = random.choice(data.possibility_words)

        e = Embed(
            title=f"Question: `{question}`",
            description="",
        )

        e.description = f"Result: {choice}"

        await interaction.response.send_message(embed=e)

    @app_commands.command(name="yes_or_no", description="Gives yes or no to your ask")
    @app_commands.describe(question="Question")
    async def yes_or_no(self, interaction: Interaction, question: str):
        choice = random.choice(["Yeah","Nope"])

        e = Embed(
            title=f"Question: `{question}`",
            description=f"Result: {choice}",
        )

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