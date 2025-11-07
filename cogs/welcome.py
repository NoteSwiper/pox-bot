import json
import os
from typing import Optional
import aiofiles
from discord import Embed, Interaction, Member, TextChannel, WelcomeChannel, app_commands
from discord.ext import commands, tasks
from logger import logger

from bot import PoxBot

class WelcomeCog(commands.Cog):
    group = app_commands.Group(name="welcome", description="Group for WelcomeCog.")

    def __init__(self, bot):
        self.bot: PoxBot = bot
        self.data = {}
        self.file_path = os.path.join(self.bot.root_path, "data/welcome.json")
    
    async def save(self):
        data_to_save = {str(k): v for k, v in self.data.items()}

        try:
            async with aiofiles.open(self.file_path, mode='w+', encoding='utf-8') as f:
                await f.write(json.dumps(data_to_save, indent=4))
            logger.info("welcome.json Saved")
        except Exception as e:
            logger.exception(f"Error saving welcome.json asynchronously: {e}")
    
    async def load(self):
        if not os.path.exists(self.file_path):
            logger.warning("welcome.json not found. Starting with empty...")
            return {}
        
        try:
            async with aiofiles.open(self.file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            
            raw_data = json.loads(content)
            self.data = {int(k): v for k, v in raw_data.items()}
            logger.info("welcome.json loaded")
        except json.JSONDecodeError:
            logger.error("Error decoding JSON. Starting with empty data.")
            self.data = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Loading database...")
        await self.load()
    
    async def cog_unload(self) -> None:
        logger.info("Saving data")
        await self.save()
    
    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        is_enabled = self.data.get(member.guild.id, 0)

        if is_enabled != 0:
            await self.send_message(0,is_enabled, member)
    
    @commands.Cog.listener()
    async def on_member_leave(self, member: Member):
        is_enabled = self.data.get(member.guild.id, 0)

        if is_enabled != 0:
            await self.send_message(1,is_enabled, member)
    
    async def send_message(self, state, channel_id, member: Member):
        channel = self.bot.get_channel(channel_id)
        if channel is None: return
        if not isinstance(channel, TextChannel): return
        
        state_text = "Joined" if state == 0 else "Left"

        try:
            lines = [
                f"ID: {member.id}",
                f"Name: {member.display_name}",
                f"Created on: {member.created_at.strftime("%Y-%m-$d %H:%M")} (<t:{int(member.created_at.timestamp())}:R>)",
            ]
            if state == 1 and member.joined_at is not None: lines.append(f"Joined on: {member.joined_at.strftime("%Y-%m-$d %H:%M")} (<t:{int(member.joined_at.timestamp())}:R>)")
            lines.append(f"\nWelcome to {member.guild.name}, <@{member.id}> :)" if state == 0 else f"\nGoodbye, {member.display_name} :(")
            title = f"{member.name} has {state_text}!" if not member.bot else f"{member.name} (BOT) has {state_text}!"
            embed = Embed(title=title, description="\n".join(lines))

            embed.set_thumbnail(url=(member.display_avatar.url if member.display_avatar else member.default_avatar.url))

            return await channel.send(embed=embed)
        except Exception as e:
            logger.exception(f"Uncaught exception: {e}")
            return
    
    @group.command(name="set_channel", description="Set channel to send join / leave message.")
    @app_commands.guild_only()
    async def set_channel(self, interaction: Interaction, channel: Optional[TextChannel]):
        if interaction.guild is None: return await interaction.response.send_message("You cannot set welcome channel unless the bot is for guild.")
        
        if channel is None:
            self.data[interaction.guild.id] = 0
            await self.save()
            return await interaction.response.send_message(f"Welcome channel has been disabled.")
        else:
            self.data[interaction.guild.id] = channel.id
            await self.save()
            return await interaction.response.send_message(f"Welcome channel has been set to {channel.mention}.")
    
    @group.command(name="test", description="Run a test for welcome channel")
    @app_commands.guild_only()
    async def test_channel(self, interaction: Interaction):
        if interaction.guild is None: return await interaction.response.send_message("You cannot set welcome channel unless the bot is for guild.")
        
        is_enabled = self.data.get(interaction.guild.id, 0)

        if is_enabled != 0:
            await self.send_message(0,is_enabled, interaction.guild.me)
        else:
            return await interaction.response.send_message("Welcome channel not configured")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))