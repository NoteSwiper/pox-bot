import asyncio
import atexit
import datetime
from itertools import cycle
import os
import random
import re
import subprocess
from time import time
import traceback
import uuid
import discord
from discord.ext import commands, tasks
from edge_tts import VoicesManager, list_voices
from gtts.lang import tts_langs
from sympy import false
import stuff
import data
import aiosqlite
import profanityfilter
from logger import logger

pf = profanityfilter.ProfanityFilter()

from data import null_interactions, null_messages
class PoxBot(commands.AutoShardedBot):
    """
    Pox's discord bot
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args,**kwargs)
        
        self.launch_time = datetime.datetime.now(datetime.UTC)
        self.launch_time2 = time()
        self.handled_messages = 0
        self.db_connection = None
        self.commit_hash = ""
        self.session_uuid = uuid.uuid4()
        self.name_signature = stuff.generate_namesignature()
        self.last_commit = stuff.get_latest_commit_message()
        self.processed_interactions = 0
        self.failed_interactions = 0
        self.gtts_cache_langs = tts_langs()
        self.received_chunks = 0
        self.already_said = False
        self.swears_in_row = 0
        
        self.activity_messages = [
            "Freedom.",
            "Python.",
            "Empty.",
            "Void.",
            "Broken.",
            "Inside.",
            "Timings.",
            "Blocks.",
            "Aware.",
            "Concious.",
            "Input.",
            "Timeout.",
            "Many of.",
            "Rot in hell.",
            "It's me.",
            "It was all his fault.",
            "Deep down under the bedrock.",
            "Poor soul.",
            "Home.",
            "A broken promise.",
            "Ended his own life.",
            "Hello.",
            "Is behind you.",
            "The end is nigh.",
            "The end is null.",
            "Chill.",
            "Loudness.",
            "End.",
            "Protection.",
            "I am aware at you.",
            "I'm aware to you.",
            "I know what you doing.",
            "Hopeless.",
            "Lose.",
            "Discord.",
            "Discard.",
            "Mercy.",
            "Wander.",
            "In boiled.",
            "You're not alone.",
            "They're watching.",
            "Did you hear it?",
        ]
        
    
    async def setup_hook(self):
        self.db_connection = await aiosqlite.connect("./leaderboard.db")
        logger.debug("Database initialized")
        try:
            output = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True, check=True)
            self.commit_hash = output.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occured: {e}")
        except FileNotFoundError:
            logger.error("Git command not found. make sure to check if Git is installed.")
    
    async def on_ready(self):
        await self.change_presence(activity=discord.CustomActivity(name=""))
        stuff.setup_database("./leaderboard.db")
        
        for fname in os.listdir('./cogs'):
            if fname.endswith('.py'):
                logger.debug(f"Loading extension {fname[:-3]}")
                try:
                    await self.load_extension(f'cogs.{fname[:-3]}')
                except Exception as e:
                    logger.exception(f"Exception thrown while loading extension {fname[:-3]}.")
        
        if self.user:
            logger.info("\n".join((
                "The client is logged into a bot!",
                f"User ID: {self.user.id}",
                f"Username: {self.user.name}",
                f"Connected Guilds: {len(self.guilds)}"
            )))
        else:
            logger.info("It seems client is connected with bot, but no user object found.")
        
        logger.debug("Syncing commands...")
        try:
            await self.tree.sync()
        except discord.HTTPException as e:
            logger.error(f"HTTPException thrown while trying to sync commands: {e}")
        except Exception as e:
            logger.exception(f"Unexcepted error thrown!")
    
    async def on_message(self,message: discord.Message):
        self.handled_messages += 1
        
        if message.author == self.user or message.mention_everyone: return
        
        if self.user:
            if self.user.mentioned_in(message) == True or self.user in message.mentions:
                prompt = message.content.replace(f'<@{self.user.id}>','').strip()
                if not prompt: return
                
                if message.content.startswith("pox!"):
                    logger.info(f"{message.author.id}, {prompt.replace('pox!','')}")
                    await self.process_commands(message)
                else:
                    if not message.author.bot or message.author.system:
                        if pf.is_profane(prompt):
                            
                            url = os.path.dirname(__file__)
                            url2 = os.path.join(url,"images/nah.jpg")

                            with open(url2, 'rb') as f:
                                pic = discord.File(f,"nah.jpg")
                            
                            e = discord.Embed()
                            e.set_image(url="attachment://nah.jpg")
                            await message.reply(file=pic,embed=e)
                            self.already_said = True
                        else:
                            for pattern, index in null_interactions.items():
                                result = re.search(pattern, prompt)
                                if result:
                                    if index['type'] == "single":
                                        inded = null_messages[index['index']]
                                        if inded is not None:
                                            await message.reply(inded)
                                    elif index['type'] == "multi":
                                        for indexindex, index2 in enumerate(index['index']):
                                            indeed = null_messages[index2]
                                            await message.reply(indeed)
                                            if indexindex != len(index['index']) - 1:
                                                await asyncio.sleep(random.uniform(1.0,2.5))
                                    break
                            #await message.reply(prompt)
        else:
            logger.error("Couldn't find 'bot.user'")
        
        pox_count = 0
        separated_words = message.content.lower().split(" ")
        
        if self.db_connection and self.user:
            if not message.author.bot or not message.author.system:
                user_id = str(message.author.id)
                if separated_words:
                    if self.db_connection:
                        async with self.db_connection.execute("SELECT amount FROM words WHERE user_id = ?", (user_id,)) as cursor:
                            result = await cursor.fetchone()

                        if result:
                            new = result[0] + len(separated_words)
                            await self.db_connection.execute("UPDATE words SET amount = ? WHERE user_id = ?", (new, user_id))
                        else:
                            await self.db_connection.execute("INSERT INTO words (user_id, amount) VALUES (?, ?)", (user_id, len(separated_words)))

                pox_count = len([item for item in separated_words if "pox" in item])
                async with self.db_connection.execute("SELECT pox_count FROM leaderboard WHERE user_id = ?", (user_id,)) as cursor:
                    result = await cursor.fetchone()

                if result:
                    new = result[0] + pox_count
                    await self.db_connection.execute("UPDATE leaderboard SET pox_count = ? WHERE user_id = ?", (new, user_id))
                else:
                    await self.db_connection.execute("INSERT INTO leaderboard (user_id, pox_count) VALUES (?, ?)", (user_id, pox_count))
        
        if message.content.startswith("pox!"):
            self.handled_messages += 1
            logger.info(f"{message.author.id}, {message.content.replace('pox!','')}")
            await self.process_commands(message)
    
    async def on_command_error(self,ctx: commands.Context, e: commands.CommandError):
        logger.exception(f"Exception thrown: {e}!")
        embed = discord.Embed(title="Error occured!",description=f"Exception thrown while processing command: {e}")
        await ctx.reply(embed=embed)
    
    async def on_interaction(self,inter: discord.Interaction):
        if inter.type == discord.InteractionType.application_command:
            logger.info(f"{inter.user.display_name} issued {inter.command.name if inter.command else "Unknown"}!")
            if inter.command_failed:
                logger.error("The requested command thrown error!")
    
    async def close(self) -> None:
        if self.db_connection:
            await self.db_connection.commit()
            await self.db_connection.close()
            logger.debug("Database closed")
        return await super().close()
        
    def get_launch_time(self) -> datetime.datetime:
        return self.launch_time

