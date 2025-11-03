from datetime import timedelta
from typing import Optional
from discord.ext import commands
from discord import Activity, ActivityType, CustomActivity, Embed, Forbidden, Game, HTTPException, Interaction, Member, Role, Spotify, Streaming, app_commands

from bot import PoxBot

from logger import logger

class CountsGroup(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="count", description="An group for Counters.")

    @group.command(name="users", description="Get count of users.")
    @commands.guild_only()
    async def count_members(self, interaction: Interaction):
        if interaction.guild is None: return await interaction.response.send_message("The commands are usable when the bot is in guild.")

        lines = []

        members = len(interaction.guild.members)
        users = len([
            user
            for user in interaction.guild.members
            if user.bot is not True
        ])
        bots = len([
            bot
            for bot in interaction.guild.members
            if bot.bot
        ])

        lines.append("Total: {}".format(members))
        lines.append("Members: {}".format(users))
        lines.append("Bots: {}".format(bots))
        lines.append("Bot ratio: {}".format((bots / members) * 100))

        embed = Embed(title="Server counter: users & extras", description="\n".join(lines))

        await interaction.response.send_message(embed=embed)
    
    @group.command(name="roles", description="Get count of roles.")
    @commands.guild_only()
    async def count_roles(self, interaction: Interaction):
        if interaction.guild is None: return await interaction.response.send_message("The commands are usable when the bot is in guild.")

        lines = []

        roles = len(interaction.guild.roles)
        managed_roles = len([
            managed
            for managed in interaction.guild.roles
            if managed.managed or managed.is_bot_managed()
        ])

        lines.append("Roles: {}".format(roles))
        lines.append("Bot roles: {}".format(managed_roles))
        lines.append("Bot role ratio: {}".format((managed_roles / roles) * 100))

        embed = Embed(title="Server counter: roles & extras", description="\n".join(lines))
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CountsGroup(bot))