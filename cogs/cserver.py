from discord import Activity, ActivityType, CustomActivity, Embed, Game, Interaction, Member, NSFWLevel, Role, Spotify, Status, Streaming, TextChannel, app_commands
from discord.ext import commands

from typing import Optional

from bot import PoxBot
from logger import logger

class GuildGroup(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    checker_group = app_commands.Group(name="guild",description="group for checker cog")
    
    @checker_group.command(name="info", description="checks current server information")
    @app_commands.guild_only()
    async def check_server_info(self, interaction: Interaction):
        guild = interaction.guild
        
        await interaction.response.defer(thinking=True)
        
        if guild and not guild.unavailable == True:
            temp1 = {
                'ID': guild.id,
                'Description': guild.description if guild.description else "No description",
                'Preffered Locale': guild.preferred_locale.language_code,
                'Owner': guild.owner,
                'Members': guild.member_count,
                'Created on': guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'Current Shard': guild.shard_id if guild.shard_id else "Unknown",
                'Over 250?': "Yes" if guild.large == True else "No",
            }
            e = Embed(title=f"Information for {guild.name}")
        
            lines = []
            for key,value in temp1.items():
                lines.append(f"{key}: `{value}`")

            if guild.icon:
                e.set_thumbnail(url=guild.icon.url)
            
            e.description = "\n".join(lines)
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("It seems the guild unavailable.")
    
    @checker_group.command(name="nsfw_level",description="Checks if server has NSFW Level")
    @app_commands.guild_only()
    async def check_nsfw_level(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Is server NSFW?",description="")
        if interaction.guild:
            match (interaction.guild.nsfw_level):
                case NSFWLevel.default:
                    embed.description = "Not NSFW"
                case NSFWLevel.explicit:
                    embed.description = "Explicit"
                case NSFWLevel.safe:
                    embed.description = "Safe"
                case NSFWLevel.age_restricted:
                    embed.description = "Age restricted"
                case _:
                    embed.description = "Unknown"
        else:
            await interaction.followup.send("Guild not found.")
            return
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GuildGroup(bot))