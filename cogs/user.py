from datetime import timedelta
from typing import Optional
from discord.ext import commands
from discord import Activity, ActivityType, CustomActivity, Embed, Forbidden, Game, HTTPException, Interaction, Member, Role, Spotify, Streaming, app_commands

from bot import PoxBot

from logger import logger

class UserGroup(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="user", description="An group for Members.")

    @group.command(name="info", description="Get user's information.")
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
    
    
    @group.command(name="avatar", description="Display user's avatar in discord.")
    @commands.guild_only()
    async def get_user_avatar(self, interaction: Interaction, member: Member):
        await interaction.response.defer()

        embed = Embed(title=f"{member.display_name}'s Avatar")
        embed.set_image(url=member.display_avatar.url if member.display_avatar else member.default_avatar.url)

        await interaction.followup.send(embed=embed)
    
    @group.command(name="kick", description="Kick a member.")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(member="Member to kick.")
    @app_commands.describe(reason="Reason for member to give in DM.")
    @commands.guild_only()
    async def kick(self, interaction: Interaction, member: Member, reason: Optional[str] = None):
        await interaction.response.defer()
        e = Embed(title="Status")
        try:
            await member.kick(reason=(reason if reason is not None else "Reason not provided by issuer."))
            e.description = f"{member.name} has been kicked from the server."
            await interaction.followup.send(embed=e)
        except Forbidden:
            e.description = f"You do not have permission to kick {member.name}."
            await interaction.followup.send(embed=e)
        except HTTPException:
            e.description = f"The operation has failed."
            await interaction.followup.send(embed=e)
        except Exception as ex:
            e.description = f"Uncaught exception. {ex}"
            await interaction.followup.send(embed=e)
    
    @group.command(name="ban", description="Bans member from the server")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to ban")
    @app_commands.describe(reason="Reason to ban")
    @commands.guild_only()
    async def ban_member(self, ctx: Interaction, member: Member, *, reason: str = ""):
        try:
            await member.ban(reason=reason)
            await member.send(f"You're banned by {ctx.user.name}.\nReason: {reason if reason else 'No reason provided'}")
            await ctx.response.send_message(f"Banned <@{member.id}>.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to ban. {e}", ephemeral=True)
    
    @group.command(name="unban", description="Unbans member")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to unban")
    @commands.guild_only()
    async def unban_member(self, ctx: Interaction, member: Member):
        try:
            await member.unban()
            await ctx.response.send_message(f"Unbanned {member.name}.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to unban. {e}", ephemeral=True)
    
    @group.command(name="warn", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to warn")
    @app_commands.describe(reason="Reason to warn")
    @commands.guild_only()
    async def warn_member(self, ctx: Interaction, member: Member, *, reason: str = ""):
        try:
            await member.send(f"You're warned by {ctx.user.name}.\n\nReason: `{reason}`")
            await ctx.response.send_message(f"Warned <@{member.id}>.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to warn. {e}")
            logger.error(f"Exception occured. {e}")
    
    @group.command(name="timeout", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to time-out")
    @app_commands.describe(reason="Reason to time-out")
    @app_commands.describe(length="Length of time-out (minutes)")
    @commands.guild_only()
    async def timeout_member(self, ctx: Interaction, member: Member, reason: str = '', length: int = 1):
        await member.timeout(timedelta(minutes=length), reason=f"You're timed out. \"{reason if reason else "No reason provided from source"}\", Requested by {ctx.user.name}")
        await ctx.response.send_message(f"Timed out {member.mention} for {length} minutes.")
    
    @group.command(name="untimeout", description="Un-timeout member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to remove timeout")
    @commands.guild_only()
    async def untimeout_member(self, ctx: Interaction, member: Member):
        await member.edit(timed_out_until=None)
        await ctx.response.send_message(f"Took the timeout for {member.mention}.")

    @group.command(name="list", description="Returns total members")
    @commands.guild_only()
    async def get_list_members(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Mmembers in this server",description="")
        
        if interaction.guild:
            embed.description = ', '.join([
                f"<@{m.id}>"
                for m in interaction.guild.members
            ])
        else:
            embed.description = "You're not in guild."
            await interaction.followup.send(embed=embed)
            return
        
        await interaction.followup.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(UserGroup(bot))