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
        is_enabled2 = self.data.get(member.guild.id)

        if is_enabled2:
            is_enabled = is_enabled2.get('welcome', 0)
            rule_channel_id = is_enabled2.get('rules', 0)

            if is_enabled != 0:
                await self.send_message(0,is_enabled, member, rule_channel_id)
    
    @commands.Cog.listener()
    async def on_member_leave(self, member: Member):
        is_enabled2 = self.data.get(member.guild.id)

        if is_enabled2:
            is_enabled = is_enabled2.get('welcome', 0)

            if is_enabled != 0:
                await self.send_message(1,is_enabled, member)
    
    async def send_message(self, state, channel_id: int, member: Member, rule_channel_id: Optional[int] = None):
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
            rules_for = ""
            if isinstance(rule_channel_id, int) and rule_channel_id != 0:
                channel2 = self.bot.get_channel(rule_channel_id)
                if isinstance(channel2, TextChannel):
                    rules_for = f"Before chatting with others, please read {channel2.mention}!"
            lines.append(f"\nWelcome to {member.guild.name}, <@{member.id}> :)" if state == 0 else f"\nGoodbye, {member.display_name} :(")
            if state == 0: lines.append(rules_for)
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
        
        self.data.setdefault(interaction.guild.id, {})

        if channel is None:
            self.data[interaction.guild.id]['welcome'] = 0
            await self.save()
            return await interaction.response.send_message(f"Welcome channel has been disabled.")
        else:
            self.data[interaction.guild.id]['welcome'] = channel.id
            await self.save()
            return await interaction.response.send_message(f"Welcome channel has been set to {channel.mention}.")
    
    @group.command(name="test", description="Run a test for welcome channel")
    @app_commands.guild_only()
    async def test_channel(self, interaction: Interaction):
        if interaction.guild is None: return await interaction.response.send_message("You cannot set welcome channel unless the bot is for guild.")
        
        is_enabled2 = self.data.get(interaction.guild.id)

        if not is_enabled2: return await interaction.response.send_message("You've not setup welcome feature.")

        is_enabled = is_enabled2.get('welcome', 0)
        rule_channel_id = is_enabled2.get('rules', 0)

        if is_enabled != 0:
            await self.send_message(0,is_enabled, interaction.guild.me, rule_channel_id)
            return await interaction.response.send_message(f"Test join message sent!")
        else:
            return await interaction.response.send_message("Welcome channel not configured.")
    
    @group.command(name="set_rules_channel", description="Sets rule channel for adding link in it.")
    @app_commands.guild_only()
    async def set_rule_channel(self, interaction: Interaction, channel: TextChannel):
        if interaction.guild is None: return await interaction.response.send_message("You cannot set welcome channel unless the bot is for guild.")
        
        self.data.setdefault(interaction.guild.id, {})

        if channel is None:
            self.data[interaction.guild.id]['rules'] = 0
            await self.save()
            return await interaction.response.send_message(f"Rules channel for welcome message has been disabled.")
        else:
            self.data[interaction.guild.id]['rules'] = channel.id
            await self.save()
            return await interaction.response.send_message(f"Rules channel for welcome message has been set to {channel.mention}.")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))