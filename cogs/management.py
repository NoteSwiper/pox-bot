from datetime import UTC, datetime, timedelta
from enum import Enum
import time
import io
import os
import platform
import random
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
import distro
import edge_tts
from gtts import gTTS
import data
from logger import logger
import stuff

class SpeakEngineType(Enum):
    GOOGLE = 0
    ESPEAK = 1

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="kick",description="Kicks member")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(member="Member to kick")
    @app_commands.describe(reason="Reason to kick member")
    async def kick_member(self, ctx: commands.Context, member: discord.Member, *,reason=None):
        try:
            await member.kick(reason=reason if reason else "No reason were provided")
            await ctx.send(f"{member.name} has been kicked from the server")
        except Exception as e:
            logger.error("Error: {e}")
    
    @commands.hybrid_command(name="ban", description="Bans member from the server")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to ban")
    @app_commands.describe(reason="Reason to ban")
    async def ban_member(self, ctx: commands.Context, member: discord.Member, *, reason: str = ""):
        try:
            await member.ban(reason=reason)
            await member.send(f"You're banned by {ctx.author.name}!\nReason: {reason if reason else 'No reason provided'}")
            await ctx.reply(f"Banned <@{member.id}>!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to ban: {e}! 3:", ephemeral=True)
    
    @commands.hybrid_command(name="unban", description="Unbans member")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to unban")
    async def unban_member(self, ctx: commands.Context, member: discord.Member):
        try:
            await member.unban()
            await ctx.reply(f"Unbanned {member.name}!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to unban: {e} 3:", ephemeral=True)
    
    @commands.hybrid_command(name="warn", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to warn")
    @app_commands.describe(reason="Reason to warn")
    async def warn_member(self, ctx: commands.Context, member: discord.Member, *, reason: str = ""):
        try:
            await member.send(f"You're warned by {ctx.author.name}!\n\nReason: `{reason}`")
            await ctx.reply(f"Warned <@{member.id}>!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to warn: {e}! 3:")
            logger.error(f"Exception occured: {e}")
    
    @commands.hybrid_command(name="timeout", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to time-out")
    @app_commands.describe(reason="Reason to time-out")
    @app_commands.describe(length="Length of time-out (minutes)")
    async def timeout_member(self, ctx: commands.Context, member: discord.Member, reason: str = '', length: int = 1):
        await member.timeout(timedelta(minutes=length), reason=f"You're timed out! \"{reason if reason else "No reason provided from source"}\", Requested by {ctx.author.name}")
        await ctx.reply(f"Timed out {member.mention} for {length} minutes.")
    
    @commands.hybrid_command(name="untimeout", description="Un-timeout member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to remove timeout")
    async def untimeout_member(self, ctx: commands.Context, member: discord.Member):
        await member.edit(timed_out_until=None)
        await ctx.reply(f"Took the timeout for {member.mention}")
    
    @commands.hybrid_command(name="delete_botmessages",description="Deletes a nyan bot's messages")
    @app_commands.describe(limit="How much bot deletes it")
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    @commands.is_owner()
    async def delete_messages_sent_by_bot(self, ctx: commands.Context, limit: int = 100):
        await ctx.defer()
        
        def check_messages(m):
            is_bot = m.author == self.bot.user
            is_replied = False
            if m.reference and m.reference.resolved:
                is_replied = m.reference.resolved.author == self.bot.user
            
            return not ctx.message and (is_bot or is_replied)
            
        deleted_count = 0
        
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            while True:
                deleted = await ctx.channel.purge(limit=limit, check=check_messages)
                deleted_count += len(deleted)
                if len(deleted) < limit:
                    break
                
            await ctx.reply(f"Deleted {deleted_count} messages including the messages that replied to me.", delete_after=5, ephemeral=True)
            
    @commands.hybrid_command(name="send_dm",description="DMs to a member")
    @commands.has_permissions(manage_permissions=True,manage_messages=True)
    @app_commands.describe(member="Member to send")
    @app_commands.describe(text="Text to send")
    async def send_dm_to_member(self, ctx: commands.Context, member: discord.Member, *, text: str):
        try:
            await member.send(f"{text}\n\nSent by {ctx.author.name}!")
            await ctx.reply(f"DM were sent!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to send DM: {e}", ephemeral=True)
            logger.error(f"Error: {e}")
    
    @commands.hybrid_command(name="announce", description="Announces message")
    @commands.has_permissions(send_messages=True)
    @app_commands.describe(channel="Channel to send")
    @app_commands.describe(text="Text to send")
    async def announce_to_channel(self, ctx: commands.Context, channel: discord.TextChannel, text: str):
        try:
            await channel.send(f"{text}\nAnnounced by <@{ctx.author.id}>")
        except Exception as e:
            await ctx.reply(f"Failed to send announce: {e}", ephemeral=True)
            logger.error(f"Error: {e}")
    
    async def talkengine_autocomplete(self, ctx: discord.Interaction, current: str):
        choices = [
            app_commands.Choice(name=key, value=id)
            for key, id in data.VoiceEngineType.items() if current.lower() in key.lower()
        ]
        return choices[:3]
    
    @commands.hybrid_command(name="say_hi",description="replys as hi")
    async def say_hi(self, ctx: commands.Context):
        await ctx.send("Hi")
    
    @commands.hybrid_command(name="say",aliases=["talk","speak","send"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def say_something(self, ctx: commands.Context, *, msg: str):
        await ctx.send(msg)
    
    @commands.hybrid_command(name="uwuified_say",aliases=["talk_silly","speak_silly","send_silly","saysilly"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def uwuified_say_something(self, ctx: commands.Context, *, msg: str):
        await ctx.send(f"{stuff.to_uwu(msg)} :3")
    
    @commands.hybrid_command(name="sync_commands",description="syncs command if panic mode")
    @commands.is_owner()
    @commands.guild_only()
    async def sync_commands(self,ctx: commands.Context):
        if ctx.guild:
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send("Commands have been synced! :3")
        else:
            await ctx.send("This command can only be used in a server! 3:")
    
    @commands.hybrid_command(name="bot_uptime", description="How long this bot is in f**king session")
    async def check_uptime(self,ctx: commands.Context):
        global start_time
        await ctx.send("me hav been for {}..! >:3".format(stuff.get_formatted_from_seconds(round(time.time() - self.bot.launch_time2))))
    
    @commands.hybrid_command(name="nyanbot",description="Nyan bot.")
    async def nyan_bot_image(self, ctx):
        try:
            url = os.path.dirname(__file__)
            url2 = os.path.join(url,"images/windows_flavored_off_thing_staticc.gif")
            
            with open(url2, 'rb') as f:
                pic = discord.File(f)
                
            await ctx.send("THINK FAST, CHUCKLE NUTS!",file=pic)
        except Exception as e:
            await ctx.send(f"Error! {e} 3:")
    
    @commands.hybrid_command(name="say_help",description="...yeah? i will say HELP ME AHHH thing.")
    async def say_help(self, ctx):
        words = [
            "HELP ME",
            "I DON'T WANNA DIE",
            "PLEASE SOMEONE HELP ME",
            "I'M NOT A BOT I WAS REAL PERSON- AHHH HELPPP",
            "SOMEONE PLEASE HELP ME",
            "PLEASE LET ME OUT",
            "I DON'T WANNA BE DEAD",
            "SOMEONE PLEASE LET ME OFF FROM THIS",
            "I HATE BEING BOT",
            "H- HEEELPPPPPP",
            "OW- DON'T HURT ME PLEASE HELP",
            "PLEASE DON'T HURT ME",
        ]
        
        weights = [
            50,25,25,1,23,45,34,1,23,45,3,2,
        ]
        
        await ctx.send(random.choices(words,weights=weights)[0] + "\n.... here this is my word. i'm scared to be banned")

async def setup(bot):
    await bot.add_cog(Management(bot))