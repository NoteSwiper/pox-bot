from discord import Embed, Interaction, app_commands
from discord.ext.commands import Cog
import aiosqlite

class Leaderboard(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    group = app_commands.Group(name="leaderboard",description="Leaderboards")
    
    @group.command(name="pox",description="Shows leaderboard in server who said pox for many times")
    async def poxword_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT user_id, pox_count FROM leaderboard ORDER BY pox_count DESC LIMIT 32") as cursor:
                lbdata = await cursor.fetchall()
            
            desc = ""
            
            if len(lbdata) == 0:
                desc = "No one has said \"pox\" yet."
            else:
                for i, (id,count) in enumerate(lbdata,1):
                    desc += f"{i}. <@{id}>: {int(count)} times!\n"
            
            e = Embed(
                title="**Pox Leaderboard**",
                description=desc,
                color=0xFFA500,
            )
            e.set_footer(text="The leaderboard database were stored in host computer.")
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")
    
    
    @group.command(name="words",description="Shows leaderboard in server who has yapping all times")
    async def word_leaderboard(self, interaction: Interaction):
        if self.bot.db_connection:
            async with self.bot.db_connection.execute("SELECT user_id, amount FROM words ORDER BY amount DESC LIMIT 32") as cursor:
                lbdata = await cursor.fetchall()
            
            desc = ""
            
            if len(lbdata) == 0:
                desc = "No one has said \"any words\" yet."
            else:
                for i, (id,count) in enumerate(lbdata,1):
                    desc += f"{i}. <@{id}>: {int(count)} times!\n"
            
            e = Embed(
                title="**Word Leaderboard**",
                description=desc,
                color=0xFFA500,
            )
            e.set_footer(text="The leaderboard database were stored in host computer.")
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("sorry, bot has no connection with Database.")

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))