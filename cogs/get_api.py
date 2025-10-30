import time
from discord import Activity, ActivityType, CustomActivity, Embed, Game, Interaction, Member, NSFWLevel, Role, Spotify, Status, Streaming, TextChannel, app_commands
from discord.ext import commands

import mojang

from roblox import UserNotFound

from bot import PoxBot

class GetAPI(commands.Cog):
    def __init__(self, bot: PoxBot):
        self.bot = bot
    
    group = app_commands.Group(name="api", description="Group for API Cog")

    minecraft_group = app_commands.Group(name="minecraft", description="Sub-group", parent=group)
    roblox_group = app_commands.Group(name="roblox", description="Sub-group")

    @minecraft_group.command(name="uuid", description="Converts Username to UUID.")
    async def username_to_uuid(self, interaction: Interaction, username: str):
        cached = self.bot.cache.get(f"mcid_{username}")
        if cached:
            await interaction.response.send_message(cached)
        else:
            cached = mojang.get_uuid(username)
            
            if cached:
                self.bot.cache.set(f"mcid_{username}",cached)
                await interaction.response.send_message(cached)
            else:
                await interaction.response.send_message("Couldn't resolve the username.")
    
    @minecraft_group.command(name="username", description="Converts UUID to Username.")
    async def uuid_to_username(self, interaction: Interaction, uuid: str):
        cached = self.bot.cache.get(f"mcuuid_{uuid}")
        if cached:
            await interaction.response.send_message(cached)
        else:
            cached = mojang.get_username(uuid)
            
            if cached:
                self.bot.cache.set(f"mcuuid_{uuid}",cached)
                await interaction.response.send_message(cached)
            else:
                await interaction.response.send_message("Couldn't resolve the UUID.")

async def setup(bot):
    await bot.add_cog(GetAPI(bot))