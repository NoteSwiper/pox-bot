from datetime import timedelta
from enum import Enum
import time
import os
from typing import Optional
import discord
from discord.ext import commands
from discord import Forbidden, Interaction, TextChannel, app_commands
from bot import PoxBot
import data
from logger import logger
import stuff

class SpeakEngineType(Enum):
    GOOGLE = 0
    ESPEAK = 1

class MessageGroup(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot

    group = app_commands.Group(name="message", description="An group for messages.")

    @group.command(name="send", description="Sends a message.")
    @commands.guild_only()
    async def send_message(self, interaction: Interaction, channel: TextChannel, message: str):
        try:
            await channel.send(f"{message}\nSent by {interaction.user.name}")
        except Forbidden:
            return await interaction.response.send_message("Failed to send: I do not have permission to send it.")
        except Exception:
            raise

    @group.command(name="mass_delete",description="Deletes messages before specified messages.")
    @app_commands.describe(limit="How much range bot will delete.")
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    @commands.guild_only()
    async def mass_delete_messages(self, interaction: Interaction, limit: Optional[int] = 100):
        await interaction.response.defer()
        
        if limit is None:
            limit = 100
        
        if isinstance(interaction.channel, discord.TextChannel):
            while True:
                deleted = await interaction.channel.purge(limit=limit)
                if len(deleted) < limit:
                    break
            
            await interaction.followup.send(f"Deleted {limit} messages.")
    
    @group.command(name="purge", description="Purges a specific amount of messages sent earlier.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge_messages(self, interaction: Interaction, limit: Optional[int] = 100):
        await interaction.response.defer()

        def check_messages(m):
            return not interaction.message

        deleted_count = 0

        if isinstance(interaction.channel, discord.TextChannel):
            deleted = await interaction.channel.purge(limit=limit if limit is not None else 100, check=check_messages)
            await interaction.followup.send(f"Purged {len(deleted)} messages.")

    @group.command(name="delete_botmessages",description="Deletes bot's messages")
    @app_commands.describe(limit="How much bot deletes it")
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    @commands.is_owner()
    @commands.guild_only()
    async def delete_messages_sent_by_bot(self, ctx: Interaction, limit: int = 100):
        await ctx.response.defer()
        
        def check_messages(m):
            is_bot = m.author == self.bot.user
            is_replied = False
            if m.reference and m.reference.resolved:
                is_replied = m.reference.resolved.author == self.bot.user
            
            return not ctx.message and (is_bot or is_replied)
            
        deleted_count = 0
        
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            while True:
                if isinstance(ctx.channel, TextChannel):
                    deleted = await ctx.channel.purge(limit=limit, check=check_messages)
                    deleted_count += len(deleted)
                    if len(deleted) < limit:
                        break
                
            await ctx.followup.send(f"Deleted {deleted_count} messages including the messages that replied to me.", ephemeral=True)
            
    @group.command(name="uwu", description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def uwuified_say_something(self, ctx: Interaction, *, msg: str):
        await ctx.response.send_message(f"{stuff.to_uwu(msg)}")
    
    @group.command(name="dm",description="DMs to a member")
    @commands.has_permissions(manage_permissions=True,manage_messages=True)
    @app_commands.describe(member="Member to send")
    @app_commands.describe(text="Text to send")
    @commands.guild_only()
    async def send_dm_to_member(self, ctx: Interaction, member: discord.Member, *, text: str):
        try:
            await member.send(f"{text}\n\nSent by {ctx.user.name}!")
            await ctx.response.send_message(f"Your message sent as DM.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to send DM. {e}", ephemeral=True)
            logger.error(f"Error. {e}")
    
async def setup(bot):
    await bot.add_cog(MessageGroup(bot))