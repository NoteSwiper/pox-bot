from discord.ext.commands import Cog
from discord import app_commands, Embed, Interaction, File
import markovify
from io import BytesIO
from datetime import datetime
import random
from os.path import dirname, join

from typing import Optional

from sympy import sequence

from bot import PoxBot
import stuff
import data

from matplotlib import pyplot as plt

class Generators(Cog):
    def __init__(self, bot):
        self.bot: PoxBot = bot

    group = app_commands.Group(name="generate", description="Generators.")
    
    @group.command(name="emoticon",description="Sends random emoticon")
    async def send_emoticon(self,ctx):
        await ctx.response.send_message(random.choice(data.emoticons))
    
    @group.command(name="idek", description="idek.")
    async def idek(self, ctx):
        await ctx.response.send_message(f"idek.")
    
    @group.command(name="nyan_cat",description="Nyan cat :D")
    async def nyan_cat_image(self, ctx: Interaction):
        try:
            url = dirname(__file__)
            url2 = join(url,"../resources/nyancat_big.gif")
            
            with open(url2, 'rb') as f:
                pic = File(f)
            
            await ctx.response.send_message("THINK FAST, CHUCKLE NUTS.",file=pic)
        except Exception as e:
            await ctx.response.send_message(f"err.type=null.error. {e}")
    
    @group.command(name="cat_jard", description="evade")
    async def cat_jard(self, interaction: Interaction):
        embed = Embed()
        embed.set_image(url="attachment://cat.png")
        
        path = join(dirname(__file__), "../resources/cat_jard.png")

        with open(path, 'rb') as f:
            pic = File(f, filename="cat.png")

        if embed:
            await interaction.response.send_message(embed=embed,file=pic)

    @group.command(name="target_close", description="Target Closing Algorithm")
    async def algorithm_closing_to_target(self, ctx: Interaction, target_value: Optional[float], concurrents: Optional[int]):
        await ctx.response.defer()
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
            await ctx.followup.send(file=file, embed=e)
    
    @group.command(name="computer_latency",description="Calculates hosted computer's latency")
    async def check_computer_latency(self, ctx: Interaction, delay: Optional[float]):
        await ctx.response.defer()
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
            await ctx.followup.send(file=file, embed=e)

    
    @group.command(name="markov", description="Generates random lines with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_text(self, ctx: Interaction, amount: Optional[int]):
        await ctx.response.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = await stuff.get_markov_dataset("m2")
        
        if not text2:
            await ctx.followup.send("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]

        lines = []
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            lines.append(result)

        await ctx.followup.send("\n".join(lines))
    
    @group.command(name="markov2", description="Generates SCP-like anomaly with Markov-chain")
    @app_commands.describe(amount="Times to generate, up to 16 iterations (lines).")
    async def generate_markovified_anomaly_text(self, ctx: Interaction, amount: Optional[int]):
        await ctx.response.defer()
        amount = stuff.clamp(amount or 1, 1, 16)
        text2 = await stuff.get_markov_dataset("m1")
        
        if not text2:
            await ctx.followup.send("Unexcepted error occured.")
            return
        
        text = "\n".join(text2)
        
        model = markovify.Text(text, state_size=3)
        
        results = [model.make_sentence() for _ in range(amount)]

        lines = []
        
        for i,result in enumerate(results):
            if not result:
                while True:
                    result = model.make_sentence()
                    if result and not result in text2:
                        break
            
            lines.append(result)

        await ctx.followup.send("\n".join(lines))

    @group.command(name="meow",description="Make me say miaw :3")
    @app_commands.describe(put_face="Enables extra face such as :3")
    async def say_meow(self, ctx: Interaction,put_face:str):
        add_face = True if put_face.lower() in ("yes", "true") else False
        arrays = data.meows_with_extraformat
        
        for index, string in enumerate(arrays):
            arrays[index] = stuff.format_extra(string)
            if add_face:
                arrays[index] = arrays[index]+" "+random.choice(data.faces)
        
        await ctx.response.send_message(f"{random.choice(arrays)}.")
    
    @group.command(name="nyan_bot",description="Nyan bot.")
    async def nyan_bot_image(self, ctx):
        try:
            url = dirname(__file__)
            url2 = join(url,"../resources/windows_flavored_off_thing_staticc.gif")
            
            with open(url2, 'rb') as f:
                pic = File(f)
                
            await ctx.response.send_message("THINK FAST, CHUCKLE NUTS.",file=pic)
        except Exception as e:
            await ctx.response.send_message(f"Error. {e}")
    
    @app_commands.command(name="hi",description="replys as hi")
    async def say_hi(self, ctx: Interaction):
        await ctx.response.send_message("Hi.")
    
    @group.command(name="collatz_graph", description="Generates Collatz Conjecture graph for a given number.")
    @app_commands.describe(number="The starting number for the Collatz sequence.")
    async def generate_collatz_graph(self, ctx: Interaction, number: int):
        def collatz_sequence(x):
            seq = [x]
            if x < 1:
                return [x]
            # Generate the Collatz sequence until reaching 1 or reaching a limit
            while x > 1 and len(seq) < 2500:
                try:
                    if x % 2 == 0:
                        x = x // 2
                    else:
                        x = 3 * x + 1
                except OverflowError:
                    break
                seq.append(x)
            return seq
        
        await ctx.response.defer()

        sequence = collatz_sequence(number)

        plt.style.use('dark_background')
        plt.figure(figsize=(12,8))
        plt.plot(sequence, marker='o')
        plt.title(f"Collatz Conjecture Sequence for {number}")
        plt.xlabel("Steps")
        plt.ylabel("Value")
        plt.grid(True)
        plt.tight_layout()
        
        buffer = BytesIO()
        
        plt.savefig(buffer, format='png')
        
        buffer.seek(0)
        
        plt.close()
        
        file = File(fp=buffer, filename='collatz_output.png')
        
        e = Embed(title=f"Collatz Conjecture Sequence for {number}")
        e.set_image(url="attachment://collatz_output.png")

        if file and e:
            await ctx.followup.send(file=file, embed=e)
        else:
            await ctx.followup.send("An error occurred while generating the graph.")
    
async def setup(bot):
    await bot.add_cog(Generators(bot))