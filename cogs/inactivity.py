import json
import random
import time
import discord
from discord.ext import commands, tasks
from discord import Activity, ActivityType, CustomActivity, Embed, Interaction, Status, app_commands

import aiofiles

from bot import PoxBot
import data
from logger import logger

class InactivityStatus(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
        self.last_activity_time = time.time()
        self.INACTIVITY_THRESHOLD = 60 * 3
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_inactivity.is_running():
            await self.bot.change_presence(
                status=Status.online,
                activity=CustomActivity(name=random.choice(data.emoticons), emoji="🥳")
            )
            self.check_inactivity.start()
    
    async def cog_unload(self) -> None:
        self.check_inactivity.cancel()
        return await super().cog_unload()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            self.last_activity_time = time.time()
    
    @tasks.loop(seconds=60.0)
    async def check_inactivity(self):
        time_since_activity = time.time() - self.last_activity_time
        current_status = self.bot.status

        if time_since_activity >= self.INACTIVITY_THRESHOLD and current_status != Status.idle:
            await self.bot.change_presence(
                status=Status.idle,
                activity=CustomActivity(name="zzz...",emoji="💤")
            )
        elif time_since_activity < self.INACTIVITY_THRESHOLD and current_status == Status.idle:
            await self.bot.change_presence(
                status=Status.online,
                activity=CustomActivity(name=random.choice(data.emoticons), emoji="🥳")
            )
async def setup(bot):
    await bot.add_cog(InactivityStatus(bot))