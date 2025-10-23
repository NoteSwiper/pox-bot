import discord
from discord import Interaction, app_commands
from discord.ext import commands
import requests
import random

from typing import Optional

import data
import stuff

def zalgo(text, Z):
    marks = list(map(chr, range(768, 879)))
    words = text.split()
    result = ' '.join(
        ''.join(
            c + ''.join(random.choice(marks) for _ in range((i // 2 + 1) * Z)) if c.isalnum() else c
            for c in word
        )
        for i, word in enumerate(words)
    )
    return result

class Converters(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    converter_group = app_commands.Group(name="converter",description="Commands for Converters")
    
    @converter_group.command(name="meow",description="makes text to MEOW MEOW.")
    @app_commands.describe(text="Text to be meowified")
    async def meowify(self, ctx: Interaction, text: str):
        await ctx.response.defer(thinking=True)
        try:
            await ctx.followup.send(stuff.meow_phrase_weighted(text))
        except Exception as e:
            await ctx.followup.send(f"Error occured! {e}")
    
    @converter_group.command(name="uwu", description="same with say_uwuify, but with mention lol")
    @app_commands.describe(text="Text to be uwuified")
    async def uwuify(self, ctx: Interaction, text: str):
        if ctx.message is None:
            await ctx.response.send_message("ctx.message is None, aborting")
            return
        else:
            await ctx.response.defer(thinking=True)
        
        try:
            await ctx.followup.send(f"<@{ctx.message.author.id}>: {stuff.to_uwu(text)}")
        except Exception as e:
            await ctx.followup.send(f"Error. {e}")
    
    @converter_group.command(name="base64", description="Makes your message into base64")
    @app_commands.describe(text="Text to be base64-ified")
    async def base64ify(self, ctx: Interaction, text: str):
        if ctx.message is None:
            await ctx.response.send_message("ctx.message is None, aborting")
            return
        else:
            await ctx.response.defer(thinking=True)
        
        try:
            await ctx.followup.send(f"<@{ctx.message.author.id}>: {stuff.base64_encode(text)}")
        except Exception as e:
            await ctx.followup.send(f"Error. {e}")
    
    @converter_group.command(name="unbase64", description="Makes your base64 message decoded")
    @app_commands.describe(text="Base64 to be textified")
    async def debase64ify(self, ctx: Interaction, text: str):
        if ctx.message is None:
            await ctx.response.send_message("ctx.message is None, aborting")
            return
        else:
            await ctx.response.defer(thinking=True)
        
        try:
            await ctx.followup.send(f"<@{ctx.message.author.id}>: {stuff.base64_decode(text)}")
        except Exception as e:
            await ctx.followup.send(f"Error. {e}")
    
    @converter_group.command(name="muffle", description="muffles your response")
    @app_commands.describe(text="Message to be MMMPHHHH-ified")
    async def mmphify(self, ctx: Interaction, text: str):
        await ctx.response.defer(thinking=True)
        try:
            await ctx.followup.send(stuff.muffle(text))
        except Exception as e:
            await ctx.followup.send(f"Error: {e} 3:")
    
    @converter_group.command(name="base7777", description="Base 7777 by galaxy_fl3x")
    async def base7777ify(self, interaction: Interaction, text: str):
        await interaction.response.defer(thinking=True)
        splitted1 = list(data.alphabet)
        splitted2 = list(data.base7777_key)
        result = ""
        for char in list(text):
            try:
                index = splitted1.index(char)
            except ValueError:
                result += char
                continue
            result += splitted2[index]
        
        await interaction.followup.send(result)

    @converter_group.command(name="unbase7777", description="Base 7777 by galaxy_fl3x")
    async def debase7777ify(self, interaction: Interaction, text: str):
        await interaction.response.defer(thinking=True)
        splitted1 = list(data.alphabet)
        splitted2 = list(data.base7777_key)
        result = ""
        for char in list(text):
            try:
                index = splitted1.index(char)
            except ValueError:
                result += char
                continue
            result += splitted1[index]
        
        await interaction.followup.send(result)

    @converter_group.command(name="glitch", description="Makes the text corrupted.")
    async def zalgo_text(self, interaction: Interaction, text:  str, level: Optional[int] = 2):
        if level is None: level = 2
        level = stuff.clamp(level, 1, 3)
        result = zalgo(text, 2)

        await interaction.response.send_message(result)
# i will add this but not this time :(
# https://colornames.org/search/json/?hex=FF0000

async def setup(bot):
    await bot.add_cog(Converters(bot))