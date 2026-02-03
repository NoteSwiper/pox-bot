import time
from discord.ext import commands, tasks
from discord import CustomActivity, Status

from bot import PoxBot
from logger import logger

class InactivityStatus(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot

        self.PRIMARY_INACTIVITY_THRESHOLD = 60 * 2.5
        self.SECONDARY_INACTIVITY_THRESHOLD = 60 * 1
        self.FINAL_INACTIVITY_THRESHOLD = 60 * 5

        self.last_activity_time = time.time()

        self.current_state = 0

        self.inactivity_enabled = False

        self.status_check_loop.start()
    
    async def cog_unload(self):
        self.status_check_loop.cancel()
    
    @tasks.loop(seconds=30.0)
    async def status_check_loop(self):
        await self.bot.wait_until_ready()
        total = len(self.bot.guilds)
        active = len([guild for guild in self.bot.guilds if not guild.unavailable])
        await self.bot.change_presence(
            status=Status.online,
            activity=CustomActivity(name=f"{total}/{active} servers")
        )
    #@tasks.loop(seconds=30.0)
    #async def status_check_loop(self):
    #    await self.bot.wait_until_ready()
    #    await self.bot.change_presence(
    #        activity=CustomActivity(name="".join(random.choices(string.ascii_letters + string.digits, k=16)))
    #    )

async def setup(bot):
    await bot.add_cog(InactivityStatus(bot))