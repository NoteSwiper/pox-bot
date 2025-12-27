from discord.ext.commands import Cog
from discord import Color, app_commands, Embed, Interaction, File
import markovify
from io import BytesIO
from datetime import datetime
import random
from os.path import dirname, join

from typing import Optional

from sympy import sequence

from bot import PoxBot
import stuff
import data

from matplotlib import pyplot as plt

class Contributors(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
        self.contributor_list = data.get_contributors()

    group = app_commands.Group(name="contributors", description="Contributors.")

    @group.command(name="list", description="Lists all contributors.")
    async def list_contributors(self, interaction: Interaction):
        embed = Embed(title="Contributors", description="Here is a list of contributors who have helped with this bot :3")

        hmmm = []

        for contributor in self.contributor_list:
            name = contributor.get("name", "Unknown")
            contribution = contributor.get("contribution", "[...]")

            hmmm.append(f"**{name}**: {contribution}")
        
        embed.description = "\n".join(hmmm)
        embed.color = Color.blue()
        
        return await interaction.response.send_message(embed=embed)
    
    @group.command(name="spy_thesinglerunc", description="Special thanks to codigoerror10014")
    async def spy_thesinglerunc(self, interaction: Interaction):
        embed = Embed(title="Special thanks to Spy_TheSingleRunc", description="She gaved ideas to the bot + she play admin house wow lol funny lala kikima-", color=Color.blue())
        embed.set_image(url="attachment://cat.png")
        embed.set_footer(text="Image credit by `codigoerror10014`.")
        
        path = join(dirname(__file__), "../resources/cat_spy.png")

        with open(path, 'rb') as f:
            pic = File(f, filename="cat.png")

        if embed:
            return await interaction.response.send_message(embed=embed,file=pic)

    @group.command(name="annayarik13alt", description=":3 (The image belongs to yarik999.999)")
    async def cat_annayarik13alt(self, interaction: Interaction):
        embed = Embed(title="Special thanks to AnnaYarik13Alt", description="He helped me suggesting the commands", color=Color.yellow())
        embed.set_image(url="attachment://cat.jpg")
        embed.set_footer(text="Image credit by `yarik999.999`. (AnnaYarik13Alt, i guess)")
        
        path = join(dirname(__file__), "../resources/cat_anna.jpg")

        with open(path, 'rb') as f:
            pic = File(f, filename="cat.jpg")

        if embed:
            return await interaction.response.send_message(embed=embed,file=pic)
    
async def setup(bot):
    await bot.add_cog(Contributors(bot))