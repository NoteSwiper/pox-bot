from discord import Activity, ActivityType, Color, CustomActivity, Embed, Game, Interaction, Member, NSFWLevel, Role, Spotify, Status, Streaming, TextChannel, app_commands
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
        
        if guild:
            temp1 = {
                'Description': guild.description if guild.description else "No description.",
                'Preferred Locale': guild.preferred_locale.language_code,
                'Owner': guild.owner.mention if guild.owner else "Unknown",
                'Members': f"{len(guild.members):,} members",
                'Created on': guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'Current Shard': guild.shard_id if guild.shard_id else "N/A",
                'Over 250?': "Yes" if guild.large == True else "No",
                'Roles': f"{len(guild.roles):,} roles",
                'Emojis': f"{len(guild.emojis):,} emojis",
                'Stickers': f"{len(guild.stickers):,} stickers",
                'Boost Level': f"Level {guild.premium_tier}",
                'Boosts': f"{guild.premium_subscription_count:,} boosts",
                'Channels': f"{len(guild.channels):,} channels",
                'Categories': f"{len(guild.categories):,} categories",
                'Chunked': f"{'Yes' if guild.chunked else 'No'}",
            }
            e = Embed(title=f"Information for {guild.name}", color=Color.blue())
            e.set_footer(text=f"Guild ID: {guild.id}")
            e.set_author(name=f"By {guild.owner.name if guild.owner else 'Unknown'}", icon_url=guild.owner.avatar.url if guild.owner and guild.owner.avatar else None)

            lines = []
            for key,value in temp1.items():
                e.add_field(name=key, value=value, inline=True)

            if guild.icon:
                e.set_thumbnail(url=guild.icon.url)
            
            e.description = "\n".join(lines)
            return await interaction.followup.send(embed=e)
        else:
            return await interaction.followup.send("Guild not found.")
    
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
            return await interaction.followup.send("Guild not found.")
        
        return await interaction.followup.send(embed=embed)
    
    @checker_group.command(name="icon", description="Gets server icon.")
    @app_commands.guild_only()
    async def get_server_icon(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        if interaction.guild and interaction.guild.icon:
            return await interaction.followup.send(embed=Embed(title="Server Icon", image=interaction.guild.icon.url))
        else:
            return await interaction.followup.send("No icon found.")

async def setup(bot):
    await bot.add_cog(GuildGroup(bot))