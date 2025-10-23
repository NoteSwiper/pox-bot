import asyncio
from io import BytesIO
import random
from typing import Optional
import os
import aiosqlite
import discord
import markovify
from matplotlib import pyplot as plt
import pytz
from datetime import datetime, UTC
from discord.ext import commands
from discord import app_commands

import stuff
import data

from logger import logger

class Silly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="say_meow",description="Make me say miaw :3")
    @app_commands.describe(put_face="Enables extra face such as :3")
    async def say_meow(self, ctx: commands.Context,put_face:str):
        add_face = True if put_face.lower() in ("yes", "true") else False
        arrays = data.meows_with_extraformat
        
        for index, string in enumerate(arrays):
            arrays[index] = stuff.format_extra(string)
            if add_face:
                arrays[index] = arrays[index]+" "+random.choice(data.faces)
        
        await ctx.send(f"{random.choice(arrays)}.")
    
    @commands.hybrid_command(name="is_owner_active",description="Check if pox is active")
    async def is_pox_active(self, ctx: commands.Context):
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
        
        await ctx.send(f"{status}\nMay the result varies by the time, cuz it is very advanced to do... also this is not accurate.")
    
    @commands.hybrid_command(name="nyan_cat",description="Nyan cat :D")
    async def nyan_cat_image(self, ctx: commands.Context):
        try:
            url = os.path.dirname(__file__)
            url2 = os.path.join(url,"../resources/nyancat_big.gif")
            
            with open(url2, 'rb') as f:
                pic = discord.File(f)
            
            await ctx.send("THINK FAST, CHUCKLE NUTS.",file=pic)
        except Exception as e:
            await ctx.send(f"err.type=null.error. {e}")
    
    @commands.hybrid_command(name="freaky_response",description="like a emoji... ahn 🥵")
    @app_commands.describe(by="A member to being freaky to me")
    async def be_freaky(self, ctx: commands.Context, by: discord.Member|None = None):
        titl = stuff.format_extra(random.choice(data.very_freaky)).format(f"<@{by.id if by else ctx.author.id}>")
        desc = "ew."
        
        await ctx.reply(f"{titl}\n{desc}")
    
    @commands.hybrid_command(name="is_owner_school_date",description="Check if owner of the bot is in school")
    async def check_if_pox_is_school_day(self,ctx):
        await ctx.send(f"Pox is {"in school day." if stuff.is_weekday(datetime.now(pytz.timezone("Asia/Tokyo"))) else "not in school day."}")
    
    @commands.hybrid_command(name="generate_emoticon",description="Sends random emoticon")
    async def send_emoticon(self,ctx):
        await ctx.send(random.choice(data.emoticons))
    
    @commands.hybrid_command(name="job_application",description="yeah")
    async def a_job_message(self, ctx):
        try:
            await ctx.send("Today, I'll be talking about one of humanity's biggest fears.")
            await asyncio.sleep(2)
            await ctx.send("# A J*B.")
        except Exception as e:
            logger.error(e)
    
    @commands.hybrid_command(name="boop_member",description="boops someone")
    @app_commands.describe(user="Member to boop")
    async def boop_member(self, ctx: commands.Context, user: discord.Member):
        await ctx.send(f"<@{user.id}> boop.")
    
    @commands.hybrid_command(name="idek", description="idek.")
    async def idek(self, ctx):
        await ctx.reply(f"idek.")
    
    @commands.hybrid_command(name="t0001",description="...")
    @app_commands.describe(id="...")
    async def pox_bad_word_thing_i_guess(self, ctx: commands.Context, id: int = 0):
        svp = ""
        desc = ""
        
        out_of_range = (id > len(data.msg_ssoa))
        
        if out_of_range:

            # swear the maker of the bot & source code   
            # i am stupid and mean-less creature ever has
            # it will not say swear at you, it only for m
            # ebecause i always wanted to be sweared by a
            # nyone but nobody hates me so i had to make 
            # this please hate me please hate me please h
            # ate me please hate me please hate me please
            # hate me please hate me please hate me pleas
            # e hate me please hate me please hate me ple
            # ase hate me please hate me please hate me p
            # lease hate me please hate me please hate me
            
            if ctx.author.id == 1321324137850994758:
                desc = "pox is dumb and idiot."
            svp = random.choice(data.err_ssoa)
        else:
            svp = data.msg_ssoa[id]
            desc = "Don't take my word. it's not directed at you."
        embed = discord.Embed(title=svp,description=desc)
        
        await ctx.reply(embed=embed)
    
    @commands.hybrid_command(name="generate_markov", description="Generates random lines with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_text(self, ctx: commands.Context, amount: Optional[int]):
        await ctx.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = stuff.get_markov_dataset("2")
        
        if not text2:
            await ctx.reply("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]
                
        e = discord.Embed(title="Generated lines")
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            e.add_field(name=f"Line {i+1}",value=result, inline=False)
        
        e.set_footer(text="Please be aware about the response may includes sensitive expressions, harmful expressions and an expression that may affect to the humans.")
        await ctx.reply(embed=e)
    
    @commands.hybrid_command(name="generate_anomaly_markov", description="Generates SCP-like anomaly with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_anomaly_text(self, ctx: commands.Context, amount: Optional[int]):
        await ctx.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = stuff.get_markov_dataset("1")
        
        if not text2:
            await ctx.reply("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]
                
        e = discord.Embed(title="Generated lines")
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            e.add_field(name=f"Line {i+1}",value=result, inline=False)
        await ctx.reply(embed=e)
    
    @commands.hybrid_command(name="target_close_algorithm", description="Target Closing Algorithm")
    async def algorithm_closing_to_target(self, ctx: commands.Context, target_value: Optional[float], concurrents: Optional[int]):
        conc = stuff.clamp(concurrents or 10, 1, 20)
        histories = [stuff.approach_target(target_value or 20) for _ in range(conc)]
        
        plt.style.use('dark_background')
        plt.figure(figsize=(12,8))
        for i, his in enumerate(histories):
            plt.plot(his, label=f"Attempt {i+1}")
        
        plt.axhline(y=target_value or 20, color='r', linestyle='--', label="Target")
        plt.title(f"Target close algorithm on {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}, with {conc} parallels")
        plt.xlabel("Steps")
        plt.ylabel("Value")
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.tight_layout()
        
        buffer = BytesIO()
        
        plt.savefig(buffer, format='png')
        
        buffer.seek(0)
        
        plt.close()
        
        file = discord.File(fp=buffer, filename='output.png')
        
        e = discord.Embed(title="Results with 'Target Close Algorithm'")
        for i,hist in enumerate(histories):
            e.add_field(name=f"Attempt #{i+1}",value=f"Length: {round(len(hist))}, Vx: \"{round(max(hist))},{round(min(hist))},{round(sum(hist)/len(hist))}\"")
        
        e.set_image(url="attachment://output.png")
        if file and e:
            await ctx.reply(file=file, embed=e)
    
    @commands.hybrid_command(name="computer_latency",description="Calculates hosted computer's latency")
    async def check_computer_latency(self, ctx: commands.Context, delay: Optional[float]):
        delay = stuff.clamp_f(delay or 150, 10,1000)/10
        delay2 = delay / 1000
        iterations = int(1/delay2)
        
        results = stuff.get_latency_from_uhhh_time(delay, iterations)

        plt.style.use('dark_background')
        plt.figure(figsize=(12,8))

        plt.plot(results,linestyle='-', color='b', label="Estimated")

        plt.axhline(y=(sum(results)/len(results)), color='r', linestyle='--', label="Avg.")
        plt.title(f"Computer Latency on {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
        plt.xlabel("Steps")
        plt.ylabel("Milliseconds")
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.tight_layout()
        
        buffer = BytesIO()
        
        plt.savefig(buffer, format='png')
        
        buffer.seek(0)
        
        plt.close()
        
        file = discord.File(fp=buffer, filename='output.png')
        
        e = discord.Embed(title="Results with 'Target Close Algorithm'")
        
        e.set_image(url="attachment://output.png")
        if file and e:
            await ctx.reply(file=file, embed=e)
        
async def setup(bot):
    await bot.add_cog(Silly(bot))