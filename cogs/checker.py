from discord import Activity, ActivityType, CustomActivity, Embed, Game, Interaction, Member, NSFWLevel, Role, Spotify, Status, Streaming, TextChannel, app_commands
from discord.ext import commands

from typing import Optional

from bot import PoxBot
from logger import logger

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    checker_group = app_commands.Group(name="check",description="group for checker cog")
    
    @checker_group.command(name="server", description="checks current server information")
    @commands.guild_only()
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
    
    @checker_group.command(name="channel", description="Checks channel information.")
    @commands.guild_only()
    async def check_channel_info(self, interaction: Interaction, channel: TextChannel):
        await interaction.response.defer(thinking=True)
        try:
            if interaction.guild:
                temp1 = {
                    'Channel ID': channel.id,
                    'Name': channel.name,
                    'Topic': channel.topic,
                    'Category': channel.category,
                    'Created on': channel.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Last message': f"{channel.last_message.content} by {channel.last_message.author.display_name}" if channel.last_message else "None",
                    'Position': channel.position,
                }
                
                e = Embed(title=f"Information for #{channel.name}")

                lines = []

                for key,value in temp1.items():
                    lines.append(f"{key}: `{value}`")
                    
                e.description = "\n".join(lines)

                await interaction.followup.send(embed=e)
            else:
                await interaction.followup.send("Channel not found.")
        except Exception as e:
            await interaction.followup.send(f"Error. {e}")
            logger.error(f"Error: {e}")

    @checker_group.command(name="user",description="Checks user information")
    @commands.guild_only()
    async def check_user_info(self, interaction: Interaction, member: Member):
        await interaction.response.defer(thinking=True)
        try:
            if interaction.guild:
                user = interaction.guild.get_member(member.id)
                if user:
                    roles = [f"{role.name}" for role in user.roles if role.name != "@everyone"]
                    temp1 = {
                        'User ID': user.id,
                        'Name': user.display_name,
                        'Bot': "True" if user.bot else "False",
                        'Created on': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'Highest role': f"{user.top_role.name}",
                        'Status': user.raw_status,
                        'Nitro since': user.premium_since.strftime("%Y-%m-%d %H:%M:%S") if user.premium_since else "It's non-nitro user.",
                        'Joined at': user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Cannot find the date when this bro joined.",
                        'Roles': ", ".join(roles)
                    }

                    if user.activities:
                        index_activity = 0
                        for activity in user.activities:
                            index_activity += 1
                            if isinstance(activity, Activity):
                                info = ""
                                match (activity.type):
                                    case ActivityType.playing:
                                        info = f"Playing {activity.name}"
                                    case ActivityType.streaming:
                                        info = f"Streaming {activity.name}"
                                    case ActivityType.listening:
                                        info = f"Listening {activity.name}"
                                    case ActivityType.watching:
                                        info = f"Watching {activity.name}"
                                    case ActivityType.custom:
                                        info = activity.name
                                    case ActivityType.competing:
                                        info = f"Competing {activity.name}"
                                    case _:
                                        info = f"Unknown Type, {activity.name}"
                                
                                temp1[f'Activity #{index_activity}'] = f"{info} ({activity.state})"
                            elif isinstance(activity, Game):
                                temp1[f'Activity #{index_activity}'] = f"Playing {activity.name} on {activity.platform}"
                            elif isinstance(activity, Streaming):
                                temp1[f'Activity #{index_activity}'] = f"Streaming {activity.name} at {activity.platform}"
                            elif isinstance(activity, CustomActivity):
                                temp1[f'Activity #{index_activity}'] = activity.name
                            elif isinstance(activity, Spotify):
                                temp1[f'Activity #{index_activity}'] = f"Listening {activity.title} by {activity.artist} in {activity.album}"
                            else:
                                temp1[f'Activity #{index_activity}'] = "Unknown."
                    
                    e = Embed(title=f"Information for {user.display_name}")

                    lines = []

                    for key,value in temp1.items():
                        lines.append(f"{key}: `{value}`")

                    if user.display_avatar:
                        e.set_thumbnail(url=user.display_avatar.url)
                    else:
                        e.set_thumbnail(url=user.default_avatar.url)
                    
                    e.description = "\n".join(lines)

                    await interaction.followup.send(embed=e)
                else:
                    await interaction.followup.send("User not found.")
            else:
                await interaction.followup.send("The command only works in guild due to issue with cache.")
        except Exception as e:
            await interaction.followup.send(f"Error. {e}")
            logger.error(f"Error: {e}")
    
    @checker_group.command(name="role",description="Checks role information")
    @commands.guild_only()
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

                e = Embed(title=f"Information for {role.name}")
                lines = []
                for key,value in temp1.items():
                    lines.append(f"{key}: `{value}`")
                if role.display_icon:
                    e.set_thumbnail(url=role.display_icon)
                
                e.description = "\n".join(lines)
                await interaction.followup.send(embed=e)
            else:
                await interaction.followup.send("Role not found.")
        except Exception as e:
            await interaction.followup.send(f"Error. {e}")
            logger.error(f"Error: {e}")
    
    @checker_group.command(name="nsfw_level",description="Checks if server has NSFW Level")
    @commands.guild_only()
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
    
    @checker_group.command(name="online",description="Returns online members. This will not shows invisible members.")
    @commands.guild_only()
    async def get_online(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Online list",description="")
        
        if interaction.guild:
            memb = []
            embed.description = '\n'.join([
                f"<@{m.id}>"
                for m in interaction.guild.members
                if m.status not in (Status.offline, Status.invisible) and not m.bot
            ])
        else:
            embed.description = "Not guild"
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
        
    @checker_group.command(name="bot_list",description="Returns bot list.")
    @commands.guild_only()
    async def get_bot_list(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Bot list",description="")
        
        if interaction.guild:
            memb = []
            embed.description = '\n'.join([
                m.name
                for m in interaction.guild.members
                if m.bot
            ])
        else:
            embed.description = "Not guild"
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
    
    @checker_group.command(name="bot_count", description="Returns total bot count.")
    @commands.guild_only()
    async def get_bot_count(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Bot count in this server",description="")
        
        if interaction.guild:
            embed.description = f"{len([
                m
                for m in interaction.guild.members
                if m.bot
            ])} is in this server."
        else:
            embed.description = "You're not in guild."
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
        
    @checker_group.command(name="usercount", description="Returns member count.")
    @commands.guild_only()
    async def get_user_count(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Member count in this server",description="")
        
        if interaction.guild:
            embed.description = f"{len([
                m
                for m in interaction.guild.members
                if not m.bot
            ])} is in this server."
        else:
            embed.description = "You're not in guild."
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
    
    @checker_group.command(name="count", description="Returns total members")
    @commands.guild_only()
    async def get_total_members(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Total members",description="")
        
        if interaction.guild:
            embed.description = f"{len(interaction.guild.members)} is in this server."
        else:
            embed.description = "You're not in guild."
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
    
    @checker_group.command(name="remaining_member_to", description="Returns remaining members to reach a value.")
    @commands.guild_only()
    async def get_remaining_members(self, interaction: Interaction, goal: Optional[int] = 100):
        await interaction.response.defer()
        if not interaction.guild:
            await interaction.followup.send("Object is not guild")
            return
        
        member_count = (len(interaction.guild.members) if interaction.guild else 0)

        if goal is None:
            goal = (round(member_count/1000)*1000)+1000
        
        e = Embed(title=f"Remaining members to reach {goal} (including bots)", description=f"Need {goal-member_count} members to reach {goal}.")

        await interaction.followup.send(embed=e)
    
    @checker_group.command(name="userstatus", description="Check user's status")
    @commands.guild_only()
    async def get_user_status(self, interaction: Interaction, member: Member):
        await interaction.response.defer()
        result = ""
        
        if interaction.guild:
            member2 = interaction.guild.get_member(member.id)
            if member2:
                result = member2.status

        e = Embed(title=f"`{member.name}`'s status",description=f"<@{member.id}> is {result}!")

        await interaction.followup.send(embed=e)
    
async def setup(bot):
    await bot.add_cog(Checker(bot))