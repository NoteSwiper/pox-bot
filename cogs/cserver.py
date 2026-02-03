from aiocache import cached
from discord import Color, Embed, Interaction, NSFWLevel, app_commands
from discord.app_commands import locale_str
from discord.ext import commands
from enum import IntFlag, auto

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
    
    @cached(300)
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
    
    @cached(300)
    @checker_group.command(name="icon", description="Gets server icon.")
    @app_commands.guild_only()
    async def get_server_icon(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        if interaction.guild and interaction.guild.icon:
            return await interaction.followup.send(embed=Embed(title="Server Icon")
                .set_image(url=interaction.guild.icon.url))
        else:
            return await interaction.followup.send("No icon found.")
    
    @cached(60)
    @checker_group.command(name="members_list", description="Retrieves memebers in this guild.")
    @app_commands.guild_install()
    async def get_members(self, interaction: Interaction, include_bot: bool = False, include_member: bool = True):
        await interaction.response.defer()

        if not interaction.guild:
            return await interaction.followup.send(embed=Embed(title="Error", description=locale_str("error.GuildOnly"), color=Color.red()))
        
        embed = Embed(
            title=f"{interaction.guild.name}'s members",
            description="",
            color=Color.green()
        )

        members = []

        if include_bot == False and include_member == False:
            embed.color = Color.red()
            embed.description = "You cannot exclude both!"
            return await interaction.followup.send(embed=embed)
        
        for member in sorted(interaction.guild.members, key=lambda r: r.top_role.position, reverse=True):
            if include_bot and member.bot:
                members.append(f"{member.top_role.mention}: {member.mention}")
            
            if include_member and not member.bot:
                members.append(f"{member.top_role.mention}: {member.mention}")
        
        if len(members) == 0:
            embed.color = Color.purple()
            embed.description = "Not found"
            return await interaction.followup.send(embed=embed)
        else:
            embed.description = "\n".join(members)
            return await interaction.followup.send(embed=embed)
    
    @cached(60)
    @checker_group.command(name="search_members", description="Searches members by keyword.")
    @app_commands.guild_install()
    async def search_members(self, interaction: Interaction, keyword: str):
        await interaction.response.defer()

        if not interaction.guild:
            return await interaction.followup.send(embed=Embed(title="Error", description=locale_str("error.GuildOnly"), color=Color.red()))
        
        embed = Embed(
            title=f"Member contains with '{keyword}' by username in {interaction.guild.name}",
            description="",
            color=Color.green()
        )

        result = []

        for member in interaction.guild.members:
            if keyword in member.name:
                result.append(member.mention)
        
        if len(result) == 0:
            embed.color = Color.purple()
            embed.description = f"User starts with {keyword} not found from this guild."
            return await interaction.followup.send(embed=embed)
        else:
            embed.description = ", ".join(result)
            return await interaction.followup.send(embed=embed)
    
    @cached(60)
    @checker_group.command(name="role_list", description="Retrieves list of roles.")
    @app_commands.guild_install()
    async def get_roles(self, interaction: Interaction):
        await interaction.response.defer()

        if not interaction.guild:
            return await interaction.followup.send(embed=Embed(title="Error", description=locale_str("error.GuildOnly"), color=Color.red()))
        
        embed = Embed(
            title=f"List of roles in {interaction.guild.name}",
            description="\n".join([role.mention for role in sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True) if not role.managed and role.name != "@everyone"]),
            color=Color.green()
        )

        return await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GuildGroup(bot))