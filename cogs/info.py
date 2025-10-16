import platform
import random
import time
from typing import Optional
from discord import Embed, Interaction, Member, User, app_commands
import discord
from discord.ext import commands
import distro

from stuff import check_map, get_formatted_from_seconds

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="info", description="Shows bot information")
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
            'Total Guilds': len(self.bot.guilds),
            'Total Chunks': len(self.bot.cached_messages),
            'Latency (ms)': round(self.bot.latency*100000)/100,
            'Shards': len(self.bot.shards if not self.bot.shards is None else "Standalone"),
		}
        
        if platform.system() == "Linux":
            os_rel = platform.freedesktop_os_release()
            if os_rel and os_rel.get("ID") == "ubuntu":
                rows_to_add['Platform'] = f"{distro.name()} {distro.version()}"
            else:
                rows_to_add['Platform'] = platform.platform()
        
        if self.bot.launch_time2:
            rows_to_add['Launch time'] = get_formatted_from_seconds(round(time.time() - self.bot.launch_time2))
        
        for k,v in rows_to_add.items():
            e.add_field(name=k,value=v,inline=True)
        
        await interaction.followup.send(embed=e)
    
    @app_commands.command(name="latest_commit_data", description="Shows bot's latest git commit.")
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
        
        e.set_footer(text="The bot is open-source. Click to this embed to access the site which is published :3")
        
        await interaction.followup.send(embed=e)
    
    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: Interaction):
        await interaction.response.defer()
        e = Embed(title="Pong!")
        rows_to_add = {
            'Latency (ms)': {round(self.bot.latency*100000)/100},
            'Shard ID': {self.bot.shard_id or "Standalone"},
            'Shards': {self.bot.shard_count or "Standalone"}
		}
        
        for k,v in rows_to_add.items():
            e.add_field(name=k,value=v,inline=True)
        
        await interaction.followup.send(embed=e)
async def setup(bot):
    await bot.add_cog(Info(bot))