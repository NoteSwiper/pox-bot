import platform
import time
from discord import Embed, Interaction, app_commands
import discord
from discord.ext import commands
import distro
from datetime import datetime
import pytz

from bot import PoxBot
from stuff import get_formatted_from_seconds
import stuff


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="info", description="Informations.")

    @group.command(name="sync_commands", description="syncs command if panic mode")
    @commands.is_owner()
    @commands.guild_only()
    async def sync_commands(self,ctx: Interaction):
        if ctx.guild:
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.response.send_message("Commands have been synced.")
        else:
            await ctx.response.send_message("This command can only be used in a server.")
    
    @group.command(name="uptime", description="How long this bot is in f**king session")
    async def check_uptime(self,ctx: Interaction):
        global start_time
        await ctx.response.send_message("I have been online for {}.".format(stuff.get_formatted_from_seconds(round(time.time() - self.bot.launch_time2))))
    
    @group.command(name="botinfo", description="I always with you :)")
    async def script_info(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        e = Embed(title="Bot Information")
        commit_hash = self.bot.commit_hash or "Unknown hash"
        last_commit_message = self.bot.last_commit or "No description"
        namesignature = self.bot.name_signature or "Unknown"
        rows_to_add = {
            'Session UUID': str(self.bot.session_uuid),
            'Version': f"Python {platform.python_version()}, discord.py {discord.__version__}",
            'Bot Version': f"git+{commit_hash} {last_commit_message}; {namesignature}" if commit_hash else "Unknown",
            'Platform': "",
            'Total messages': f"{self.bot.handled_messages} messages",
            'Total interactions': f"{self.bot.processed_interactions} / {self.bot.failed_interactions}",
            'Total Guilds': len(self.bot.guilds),
            'Total Chunks': len(self.bot.cached_messages),
            'Total Cached': f"{self.bot.cache.get_count()}",
            'Latency (ms)': round(self.bot.latency*100)/100,
            'Shards': len(self.bot.shards if not self.bot.shards is None else "Standalone"),
            'Developer': "p0x38 (NoteSwiper)",
            'I can see': str(len(self.bot.users)) + " users",
        }
        
        if platform.system() == "Linux":
            os_rel = platform.freedesktop_os_release()
            if os_rel and os_rel.get("ID") == "ubuntu":
                rows_to_add['Platform'] = f"{distro.name()} {distro.version()}"
            else:
                rows_to_add['Platform'] = platform.platform()
        else:
            rows_to_add['Platform'] = platform.platform()
        
        if self.bot.launch_time2:
            rows_to_add['Launch time'] = get_formatted_from_seconds(round(time.time() - self.bot.launch_time2))

        lines = []

        for k,v in rows_to_add.items():
            lines.append(f"{k}: {v}")
        
        e.description = "\n".join(lines)

        await interaction.followup.send(embed=e)
    
    @group.command(name="commit_data", description="Shows bot's latest git commit.")
    async def get_commit_data(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        
        commit_hash = self.bot.commit_hash or "Unknown hash"
        last_commit_message = self.bot.last_commit or "No description"
        temp1 = {
            'Commit Hash': commit_hash,
            'Commit Message': last_commit_message,
        }
        
        e = discord.Embed(title="Current git information", url="https://github.com/NoteSwiper/pox-bot")
        
        for item, value in temp1.items():
            e.add_field(name=item,value=value)
        
        e.set_footer(text="The bot is open-source. Click to this embed to access the site which is published.")
        
        await interaction.followup.send(embed=e)
    
    @group.command(name="ping", description="Pong!")
    async def ping(self, interaction: Interaction):
        await interaction.response.defer()
        e = Embed(title="Pong!")
        rows_to_add = {
            'Latency (ms)': {round(self.bot.latency*100)/100},
            'Shard ID': {self.bot.shard_id or "Standalone"},
            'Shards': {self.bot.shard_count or "Standalone"}
		}
        
        for k,v in rows_to_add.items():
            e.add_field(name=k,value=v,inline=True)
        
        await interaction.followup.send(embed=e)

    @group.command(name="pox",description="Say him 'p0x38 is retroslop >:3'")
    async def pox_message(self, ctx: discord.Interaction):
        await ctx.response.defer()
        await ctx.followup.send("p0x38 is retroslop.")

    @group.command(name="timedate", description="Shows time in bot's time")
    async def get_bot_timestamp(self, ctx: discord.Interaction):
        await ctx.response.defer()
        timec = datetime.now(pytz.timezone("Asia/Tokyo"))
        
        await ctx.followup.send(f"I'm on {datetime.strftime(timec, '%Y-%m-%d %H:%M:%S%z')}.")
    
    @group.command(name="name_signature", description="Shows temporary signature for the bot.")
    async def namesignature(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await interaction.followup.send(f"{self.bot.name_signature}; {self.bot.session_uuid}")

    @group.command(name="school_date",description="Check if owner of the bot is in school")
    async def check_if_pox_is_school_day(self,ctx):
        await ctx.response.send_message(f"Pox is {"in school day." if stuff.is_weekday(datetime.now(pytz.timezone("Asia/Tokyo"))) else "not in school day."}")
    
    @group.command(name="active",description="Check if owner of the bot is active")
    async def is_pox_active(self, ctx: Interaction):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        isWeekday = stuff.is_weekday(now)
        isFaster = stuff.is_specificweek(now,2) or stuff.is_specificweek(now,4)
        isInSchool = stuff.is_within_hour(now,7,16) if isWeekday and not isFaster else (stuff.is_within_hour(now,7,15) if isWeekday and isFaster else False)
        isSleeping = stuff.is_sleeping(now,23,7) if isWeekday else stuff.is_within_hour(now,2,12)
        status = ""
        
        if isInSchool:
            status = "Pox is in school."
        elif isSleeping:
            status = "Pox is sleeping."
        else:
            status = "Pox is sometime active."
        
        await ctx.response.send_message(f"{status}\nMay the result varies by the time, cuz it is very advanced to do... also this is not accurate.")
        
async def setup(bot):
    await bot.add_cog(Info(bot))