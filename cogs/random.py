from datetime import timedelta
import random
from typing import Optional
from discord.ext import commands
from discord import Activity, ActivityType, CustomActivity, Embed, Forbidden, Game, HTTPException, Interaction, Member, Role, Spotify, Streaming, app_commands

from bot import PoxBot

from logger import logger
from stuff import clamp

class RandomGroup(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="random", description="An group for Random.")

    @group.command(name="user", description="Returns random user(s).")
    async def random_user(self, interaction: Interaction, max_selections: Optional[int] = 1):
        if interaction.guild is None: return await interaction.response.send_message("The command only can be runned when the bot is installed in server(s).")

        if max_selections is None: max_selections = 1

        real_members = [member for member in interaction.guild.members if member.bot is not True]

        max_selections = clamp(max_selections, 1, len(real_members))

        selected_users = []

        for i in range(max_selections):
            selected_users.append(random.choice(real_members))
        
        lines = ["Selected members are:"]

        for user in selected_users:
            lines.append(f"<@{user.id}>")
            
        embed = Embed(title=":3",description="\n".join(lines))

        return await interaction.response.send_message(embed=embed)
    
    @group.command(name="fixed_number", description="Returns fixed number of user.")
    async def get_user_fixed_number(self, interaction: Interaction, member: Member):
        if interaction.guild is None: return await interaction.response.send_message("The command only can be runned when the bot is installed in server(s).")

        return await interaction.response.send_message(abs(hash(member.name)) % 9999999999)

    @group.command(name="role", description="Returns random role(s).")
    async def random_role(self, interaction: Interaction, max_selections: Optional[int] = 1):
        if interaction.guild is None: return await interaction.response.send_message("The command only can be runned when the bot is installed in server(s).")

        if max_selections is None: max_selections = 1

        max_selections = clamp(max_selections, 1, len(interaction.guild.roles))

        selected_roles = []

        for i in range(max_selections):
            selected_roles.append(random.choice(interaction.guild.roles))
        
        lines = ["Selected roles are:"]

        for role in selected_roles:
            lines.append(f"<@&{role.id}>")
            
        embed = Embed(title=":3",description="\n".join(lines))

        return await interaction.response.send_message(embed=embed)
async def setup(bot):
    await bot.add_cog(RandomGroup(bot))