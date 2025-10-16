from discord import Asset, Color, Embed, Interaction, Member, NSFWLevel, Role, Status, app_commands
from discord.ext import commands

from logger import logger

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    checker_group = app_commands.Group(name="check",description="group for checker cog")
    
    @checker_group.command(name="server", description="checks current server information")
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
            }
            
            e = Embed(
                title=f"Information for {guild.name}",
                color=Color.blue()
            )
            
            for key,value in temp1.items():
                e.add_field(name=key,value=value, inline=True)
            
            if guild.icon:
                e.set_thumbnail(url=guild.icon.url)
            
            await interaction.followup.send(embed=e)
        else:
            await interaction.followup.send("It seems the guild unavailable.")
    
    @checker_group.command(name="user",description="Checks user information")
    async def check_user_info(self, interaction: Interaction, user: Member):
        await interaction.response.defer(thinking=True)
        try:
            if user:
                roles = [f"{role.name}" for role in user.roles]
                temp1 = {
                    'User ID': user.id,
                    'Name': user.display_name,
                    'Bot': "True" if user.bot else "False",
                    'Created on': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Highest role': f"{user.top_role.name}",
                    'Status': user.raw_status,
                    'Nitro since': user.premium_since.strftime("%Y-%m-%d %H:%M:%S") if user.premium_since else "Unknown",
                    'Joined at': user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Unknown",
                    'Roles': ", ".join(roles)
                }

                e = Embed(title=f"Information for <@{user.id}>")

                for key,value in temp1.items():
                    e.add_field(
                        name=key,
                        value=value,
                        inline=True
                    )

                if user.display_avatar:
                    e.set_thumbnail(url=user.display_avatar.url)
                
                await interaction.followup.send(embed=e)
            else:
                await interaction.followup.send("User not found!")
        except Exception as e:
            await interaction.followup.send(f"Error! {e} 3:")
            logger.error(f"Error: {e}")
    
    @checker_group.command(name="role",description="Checks role information")
    async def check_role_info(self, interaction: Interaction, role: Role):
        await interaction.response.defer(thinking=True)
        try:
            if role:
                members = [f"{member.display_name}" for member in role.members]
                temp1 = {
                    'Role ID': role.id,
                    'Role Name': role.name,
                    'Role Color': role.color,
                    'Created on': role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Managed Role?': "Yeah" if role.managed == True else ("Nah" if role.managed == False else "I dunno"),
                    "Can be mentioned": "Yup but don't spam it please" if role.mentionable == True else ("Nope" if role.mentionable == False else "I dunno"),
                    "It shown in member list?": "Ye" if role.hoist == True else ("Nuh uh" if role.hoist == False else "I dunno"),
                    "Position": role.position or "IDK",
                    "Members": ", ".join(members)
                }

                e = Embed(title=f"Information for <@{role.id}>")

                for key,value in temp1.items():
                    e.add_field(
                        name=key,
                        value=value,
                        inline=True
                    )

                if role.display_icon and isinstance(role.display_icon, Asset):
                    e.set_thumbnail(url=role.display_icon.url)
                
                await interaction.followup.send(embed=e)
            else:
                await interaction.followup.send("User not found!")
        except Exception as e:
            await interaction.followup.send(f"Error! {e} 3:")
            logger.error(f"Error: {e}")
    
    @checker_group.command(name="nsfw_level",description="Checks if server has NSFW Level")
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
    
    @checker_group.command(name="online",description="Returns online members")
    async def get_online(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Online list",description="")
        
        if interaction.guild:
            memb = []
            embed.description = '\n'.join([
                m.name
                for m in interaction.guild.members
                if m.status not in (Status.offline, Status.invisible) and not m.bot
            ])
        else:
            embed.description = "Not guild"
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Checker(bot))