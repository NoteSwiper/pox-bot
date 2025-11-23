from enum import member
import json
import discord
from discord.ext import commands
from discord import Embed, Interaction, app_commands

import aiofiles

from bot import PoxBot
from logger import logger

class Blacklister(commands.Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    group = app_commands.Group(name="blacklist", description="Blacklister.")

    word_group = app_commands.Group(name="word", description="Blacklisted word management.", parent=group)
    chat_group = app_commands.Group(name="chat", description="Blacklisted chat management.", parent=group)
    member_group = app_commands.Group(name="member", description="Blacklisted member management.", parent=group)

    @chat_group.command(name="add", description="Adds blacklisted chat to server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def add_blacklisted_chat(self, interaction: Interaction, channel: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)

        blacklisted = self.bot.blacklisted_words

        serverchats = blacklisted.get(guild_id, {}).get('chat', [])

        if str(channel.id) in serverchats:
            await interaction.followup.send(f"The chat {channel.mention} is already blacklisted.")
            return
        
        serverchats.append(str(channel.id))
        blacklisted[guild_id] = serverchats

        return await interaction.followup.send(f"Added {channel.mention} to the server's blacklisted chats.\nIf you want this feature works, make sure the bot to higher than members.")
    
    @chat_group.command(name="remove", description="Removes blacklisted chat from server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def remove_blacklisted_chat(self, interaction: Interaction, channel: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)

        blacklisted = self.bot.blacklisted_words

        serverchats = blacklisted.get(guild_id, {}).get('chat', [])

        if not str(channel.id) in serverchats:
            await interaction.followup.send(f"The chat {channel.mention} is not blacklisted.")
            return
        
        serverchats.remove(str(channel.id))

        blacklisted[guild_id] = serverchats

        await interaction.followup.send(f"Removed {channel.mention} from the server's blacklisted chats.\nIf you want this feature works, make sure the bot to higher than members.")
    
    @chat_group.command(name="list", description="Lists banned chats.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True, manage_guild=True)
    async def list_blacklisted_chats(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        embed = Embed(title="Banned chats")
        lines = ["Banned chats in this server listed below:"]
        banned_chats = self.bot.blacklisted_words.get(str(interaction.guild.id), {}).get('chat', [])

        if len(banned_chats) > 0:
            for channel_id in banned_chats:
                channel = interaction.guild.get_channel(int(channel_id))
                if channel is not None:
                    lines.append(channel.mention)
                else:
                    lines.append(f"Deleted Channel (ID: {channel_id})")
        else:
            lines.append("No banned chats were found from Database.")
        
        embed.description = "\n".join(lines)
        embed.set_footer(text="If you want this feature works, make sure the bot to higher than members.")

        await interaction.response.send_message(embed=embed)
    
    @member_group.command(name="add", description="Adds blacklisted member to server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def add_blacklisted_member(self, interaction: Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)

        blacklisted = self.bot.blacklisted_words

        servermembers = blacklisted.get(guild_id, {}).get('member', [])

        if str(member.id) in servermembers:
            await interaction.followup.send(f"The member {member.mention} is already blacklisted.")
            return
        
        servermembers.append(str(member.id))
        blacklisted[guild_id] = servermembers

        await interaction.followup.send(f"Added {member.mention} to the server's blacklisted members.\nIf you want this feature works, make sure the bot to higher than members.")
    
    @member_group.command(name="remove", description="Removes blacklisted member from server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def remove_blacklisted_member(self, interaction: Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)

        blacklisted = self.bot.blacklisted_words

        servermembers = blacklisted.get(guild_id, {}).get('member', [])

        if not str(member.id) in servermembers:
            await interaction.followup.send(f"The member {member.mention} is not blacklisted.")
            return
        
        servermembers.remove(str(member.id))

        blacklisted[guild_id] = servermembers

        await interaction.followup.send(f"Removed {member.mention} from the server's blacklisted members.\nIf you want this feature works, make sure the bot to higher than members.")
    
    @member_group.command(name="list", description="Lists banned members.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True, manage_guild=True)
    async def list_blacklisted_members(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        embed = Embed(title="Banned members")
        lines = ["Banned members in this server listed below:"]
        banned_members = self.bot.blacklisted_words.get(str(interaction.guild.id), {}).get('member', [])

        if len(banned_members) > 0:
            for member_id in banned_members:
                member = interaction.guild.get_member(int(member_id))
                if member is not None:
                    lines.append(member.mention)
                else:
                    lines.append(f"Left Member (ID: {member_id})")
        else:
            lines.append("No banned members were found from Database.")
        
        embed.description = "\n".join(lines)
        embed.set_footer(text="If you want this feature works, make sure the bot to higher than members.")

        await interaction.response.send_message(embed=embed)

    @word_group.command(name="add", description="Adds blacklisted word to server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def add_blacklisted_word(self, interaction: Interaction, word: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)
        word = word.lower()

        blacklisted = self.bot.blacklisted_words

        serverwords = blacklisted.get(guild_id, {}).get('word', [])

        if word in serverwords:
            await interaction.followup.send(f"The word {word} is already blacklisted.")
            return
        
        serverwords.append(word)
        blacklisted[guild_id] = serverwords

        await interaction.followup.send(f"Added {word} to the server's blacklisted words.\nIf you want this feature works, make sure the bot to higher than members.")
    

    @word_group.command(name="remove", description="Removes blacklisted word from server.")
    @app_commands.checks.has_permissions(manage_messages=True,manage_guild=True)
    @app_commands.guild_only()
    async def remove_blacklisted_word(self, interaction: Interaction, word: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)
        word = word.lower()

        blacklisted = self.bot.blacklisted_words

        serverwords = blacklisted.get(guild_id, {}).get('word', [])

        if not word in serverwords:
            await interaction.followup.send(f"The word {word} is not blacklisted.")
            return
        
        serverwords.remove(word)

        blacklisted[guild_id] = serverwords

        await interaction.followup.send(f"Removed {word} from the server's blacklisted words.\nIf you want this feature works, make sure the bot to higher than members.")
    
    @word_group.command(name="list", description="Lists banned words.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True, manage_guild=True)
    async def list_blacklisted_words(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in Guild-install.")
            return
        embed = Embed(title="Banned words")
        lines = ["Banned words in this server listed below:"]
        banned_words = self.bot.blacklisted_words.get(str(interaction.guild.id), {}).get('word', [])

        if len(banned_words) > 0:
            for word in banned_words:
                lines.append(word)
        else:
            lines.append("No banned words were found from Database.")
        
        embed.description = "\n".join(lines)
        embed.set_footer(text="If you want this feature works, make sure the bot to higher than members.")

        await interaction.response.send_message(embed=embed)
    
    
async def setup(bot):
    await bot.add_cog(Blacklister(bot))