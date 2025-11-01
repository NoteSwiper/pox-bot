from discord.ext.commands import Cog
from discord import app_commands, Embed, Interaction, File
import markovify
from io import BytesIO
from datetime import datetime

from typing import Optional

from bot import PoxBot
import stuff

from matplotlib import pyplot as plt

class Generators(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot
    
    
    @app_commands.command(name="target_close", description="Target Closing Algorithm")
    async def algorithm_closing_to_target(self, ctx: Interaction, target_value: Optional[float], concurrents: Optional[int]):
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
        
        file = File(fp=buffer, filename='output.png')
        
        e = Embed(title="Results with 'Target Close Algorithm'")
        for i,hist in enumerate(histories):
            e.add_field(name=f"Attempt #{i+1}",value=f"Length: {round(len(hist))}, Vx: \"{round(max(hist))},{round(min(hist))},{round(sum(hist)/len(hist))}\"")
        
        e.set_image(url="attachment://output.png")
        if file and e:
            await ctx.response.send_message(file=file, embed=e)
    
    @app_commands.command(name="computer_latency",description="Calculates hosted computer's latency")
    async def check_computer_latency(self, ctx: Interaction, delay: Optional[float]):
        delay = stuff.clamp_f(delay or 150, 10,1000) / 10
        delay2 = delay / 1000
        iterations = int(1/delay2)
        
        results = stuff.get_latency_from_uhhh_time(delay, iterations)

        plt.style.use('dark_background')
        plt.figure(figsize=(12,8))

        plt.plot(results,linestyle='-', color='b', label="Estimated")

        plt.axhline(y=(sum(results) / len(results)), color='r', linestyle='--', label="Avg.")
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
        
        file = File(fp=buffer, filename='output.png')
        
        e = Embed(title="Results with 'Target Close Algorithm'")
        
        e.set_image(url="attachment://output.png")
        if file and e:
            await ctx.response.send_message(file=file, embed=e)

    
    @app_commands.command(name="generate_markov", description="Generates random lines with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_text(self, ctx: Interaction, amount: Optional[int]):
        await ctx.response.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = stuff.get_markov_dataset("2")
        
        if not text2:
            await ctx.followup.send("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]
                
        e = Embed(title="Generated lines")
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            e.add_field(name=f"Line {i+1}",value=result, inline=False)
        
        e.set_footer(text="Please be aware about the response may includes sensitive expressions, harmful expressions and an expression that may affect to the humans.")
        await ctx.followup.send(embed=e)
    
    @app_commands.command(name="generate_anomaly_markov", description="Generates SCP-like anomaly with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_anomaly_text(self, ctx: Interaction, amount: Optional[int]):
        await ctx.response.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = stuff.get_markov_dataset("1")
        
        if not text2:
            await ctx.followup.send("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]
                
        e = Embed(title="Generated lines")
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            e.add_field(name=f"Line {i+1}",value=result, inline=False)
        await ctx.followup.send(embed=e)

async def setup(bot):
    await bot.add_cog(Generators(bot))