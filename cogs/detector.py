import random
from typing import Optional
from discord import Embed, Interaction, Member, User, app_commands
from discord.ext import commands

from stuff import check_map

class Detector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    detector_group = app_commands.Group(name="detect", description="A group for detector cogs")
    
    @detector_group.command(name="gay", description="Check if member is gay")
    @app_commands.describe(member="Member to check")
    async def gay_detector(self, interaction: Interaction, member: Member):
        await interaction.response.defer(thinking=True)
        randum = int(random.random()*100)
        dac = check_map(randum,100)
        
        e = Embed(title=f"Is {member.name} gay?",description=f"Result: {dac} gay.")
        
        await interaction.followup.send(embed=e)
    
    @detector_group.command(name="femboy", description="Check if member is femboy")
    @app_commands.describe(member="Member to check")
    async def femboy_detector(self, interaction: Interaction, member: Member):
        await interaction.response.defer(thinking=True)
        randum = int(random.random()*100)
        dac = check_map(randum,100)
        
        e = Embed(title=f"Is {member.name} femboy?",description=f"Result: {dac} femboy.")
        
        await interaction.followup.send(embed=e)
    
    @detector_group.command(name="freaky", description="Check if member is freaky")
    @app_commands.describe(member="Member to check")
    async def freaky_detector(self, interaction: Interaction, member: Member):
        await interaction.response.defer(thinking=True)
        randum = int(random.random()*100)
        dac = check_map(randum,100)
        
        e = Embed(title=f"Is {member.name} freaky?",description=f"Result: {dac} freaky.")
        
        await interaction.followup.send(embed=e)
    
    @detector_group.command(name="vibe",description="Checks how's vibing")
    @app_commands.describe(member="Member to check")
    async def vibe_check(self, interaction: Interaction, member: Optional[Member|User] = None):
        await interaction.response.defer(thinking=True)
        if member is None:
            if not interaction.message is None:
                member = interaction.message.author
            else:
                await interaction.followup.send("Message isn't available")
                return
        
        rand = round(random.randrange(0,100))
        
        e = Embed(title=f"How much {member.name} is vibing", description=f"Result: {rand} %.")
        await interaction.followup.send(embed=e)
    
    @detector_group.command(name="custom", description="Check if member is something specified in command")
    @app_commands.describe(member="Member to check")
    async def custom_detection(self, interaction: Interaction, member: Member, *, custom: str):
        await interaction.response.defer(thinking=True)
        randum = int(random.random()*100)
        dac = check_map(randum,100)
        
        e = Embed(title=f"Is {member.name} {custom}?",description=f"Result: {dac} {custom}.")
        
        await interaction.followup.send(embed=e)
    
async def setup(bot):
    await bot.add_cog(Detector(bot))