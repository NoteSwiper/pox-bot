import discord
from discord.ext.commands import Cog
from discord import app_commands, Embed, Interaction

from bot import PoxBot

class Feedback(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    @app_commands.command(name="feedback", description="Feedback.")
    async def feedback(self, interaction: Interaction):
        e = Embed()
        e.description = "If you have any suggestions to the bot, you have to access google forms and write it.\nYou can access by clicking the title"
        e.set_author(name="Click here to go Google Forms", url="https://forms.gle/krTyQPdSuNBzVYuS6")

        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Feedback(bot))