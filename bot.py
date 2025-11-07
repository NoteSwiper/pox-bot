import asyncio
import datetime
import os
import random
import re
import subprocess
from time import time
import uuid
import aioconsole
import discord
from discord.ext import commands
from gtts.lang import tts_langs
from classes import Cache, EmoticonGenerator
import stuff
import data
import aiosqlite
import profanityfilter
import roblox
from logger import logger, interact_logger
from discord import Forbidden, HTTPException, Interaction, MissingApplicationID, TextChannel, app_commands

import aiofiles
import json

from data import null_interactions, null_messages

class PoxBot(commands.AutoShardedBot):
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
        self.active_games = {}
        self.activity_messages = []
        self.invites = []
        self.cache = Cache(60*60*24)
        self.roblox_client = roblox.Client()
        self.profanity_filter = profanityfilter.ProfanityFilter()
        self.blacklisted_words = {}
        self.servers_data = {}
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.available_togglers = [
            "delete_message_with_swears",
            "enable_level_notify",
            "anti_spam_message",
            "enable_bot_predefined_autoreply"
        ]
        self.spam_time_window = 5
        self.max_messages_per_window = 5
        self.user_message_timestamps = {}
        self.emoticon_generator = EmoticonGenerator()
        self.custom_activity = os.path.join(self.root_path, "resources/what_2.txt")
    
    async def setup_hook(self):
        stuff.setup_database("./leaderboard.db")
        
        self.db_connection = await aiosqlite.connect("./leaderboard.db")
        logger.debug("Database initialized")

        try:
            async with aiofiles.open('data/blacklisted_words.json', 'r+') as f:
                content = await f.read()
                self.blacklisted_words = json.loads(content)
                logger.debug(self.blacklisted_words)
        except FileNotFoundError:
            self.blacklisted_words = {}
        except json.JSONDecodeError:
            logger.error("blacklisted_words.json is empty or invalid.")
            self.blacklisted_words = {}

        try:
            async with aiofiles.open('data/server_data.json', 'r+') as f:
                content = await f.read()
                self.servers_data = json.loads(content)
                logger.debug(self.servers_data)
        except FileNotFoundError:
            self.servers_data = {}
        except json.JSONDecodeError:
            logger.error("server_data.json is empty or invalid.")
            self.servers_data = {}
        """
        try:
            if self.custom_activity is not None:
                with open(self.custom_activity, 'r') as f:
                    self.activity_messages = f.read().splitlines()
            else:
                with open("resources/what.txt",'r') as f:
                    self.activity_messages = f.read().splitlines()
        except Exception as e:
            logger.exception(f"Error occured while trying to get activity message list: {e}")
        """
        try:
            output = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True, check=True)
            self.commit_hash = output.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occured: {e}")
        except FileNotFoundError:
            logger.error("Git command not found. make sure to check if Git is installed.")
        
        for fname in os.listdir('./cogs'):
            if fname.endswith('.py'):
                logger.debug(f"Loading extension {fname[:-3]}.")

                try:
                    await self.load_extension(f"cogs.{fname[:-3]}")
                    logger.debug(f"Successfully loaded {fname[:-3]}.")
                except commands.ExtensionNotLoaded as e:
                    logger.exception(f"Extension {fname[:-3]} was not loaded due to {e}.")
                except commands.ExtensionNotFound:
                    logger.exception(f"Extension {fname[:-3]} was not found from cogs folder.")
                except commands.NoEntryPointError:
                    logger.exception(f"Extension {fname[:-3]} has no entrypoint to load.")
                except commands.ExtensionFailed as e:
                    logger.exception(f"Extension {fname[:-3]} has failed to load due to {e}.")
                except Exception as e:
                    logger.exception(f"Uncaught exception thrown while reloading, due to {e}.")

    async def on_ready(self):
        if self.user:
            logger.info("\n".join((
                "The client is logged into a bot!",
                f"User ID: {self.user.id}",
                f"Username: {self.user.name}",
                f"Connected Guilds: {len(self.guilds)}",
                f"Guilds: {", ".join([guild.name for guild in self.guilds])}"
            )))
        else:
            logger.info("It seems client is connected with bot, but no user object found.")

        try:
            synced = await self.tree.sync()
            logger.info(f"Synchronized {len(synced)} commands.")
        except app_commands.CommandSyncFailure:
            logger.exception("CommandSyncFailure: Invalid command data")
        except Forbidden:
            logger.error("Forbidden: The bot doesn't have permission to use `application.commands`")
        except MissingApplicationID:
            logger.error("MissingApplicationID: The application ID is empty or missing")
        except app_commands.TranslationError:
            logger.exception("TranslationError: Error occured while translating commands")
        except HTTPException:
            logger.error("HTTPException: Failed to sync commands")
            
    async def on_message(self,message: discord.Message):
        self.handled_messages += 1
        
        if message.author == self.user or message.mention_everyone: return
        
        if message.guild:
            blacklisted_words = self.blacklisted_words.get(str(message.guild.id))
            
            has_permission = message.channel.permissions_for(message.guild.me).manage_messages
            is_author_lower = message.author.top_role < message.guild.me.top_role if isinstance(message.author, discord.Member) else True
            
            try:
                content = message.content.lower()                
                if blacklisted_words is not None:
                    combined_pattern = r'\b(' + '|'.join(blacklisted_words) + r')\b'
                    is_match = re.search(combined_pattern, content)

                    if is_match and is_author_lower and has_permission:
                        logger.debug(f"Blacklisted word has found from message; deleting")
                        await message.delete()
                elif self.servers_data[str(message.guild.id)]['delete_message_with_swears'] == True:
                    if data.filter_pattern.search(content) and is_author_lower and has_permission:
                        logger.debug(f"Blacklisted word has found from message; deleting")
                        await message.delete()
                if self.servers_data[str(message.guild.id)]['anti_spam_message'] == True:
                    user_id = message.author.id
                    current_time = time()
        
                    if user_id not in self.user_message_timestamps:
                        self.user_message_timestamps[user_id] = []
                    
                    self.user_message_timestamps[user_id].append(current_time)
        
                    self.user_message_timestamps[user_id] = [
                        t for t in self.user_message_timestamps[user_id]
                        if t > current_time - self.spam_time_window
                    ]

                    logger.info(f"{len(self.user_message_timestamps[user_id])}/{self.max_messages_per_window}")
        
                    if len(self.user_message_timestamps[user_id]) > self.max_messages_per_window:
                        try:
                            logger.warn("Spamming detected; deleting spam messages...")
                            await message.delete()
                        except Forbidden:
                            logger.error("I can't delete message; not enough permission")
            except KeyError:
                pass
            except Exception as e:
                logger.exception(f"Uncaught exception: {e}")

        #if message.guild and message.guild.id == 1382319176735264819:
        #    content = message.content.lower()
        #    if data.filter_pattern.search(content):
        #        await message.delete()
            #if pf.is_profane(content) or any(word in content for word in data.bad_words):
            #    await message.delete()

        if self.user:
            if self.user.mentioned_in(message) == True or self.user in message.mentions:
                prompt = message.content.replace(f'<@{self.user.id}>','').strip()
                if not prompt: return
                
                if message.content.startswith("pox!"):
                    logger.info(f"{message.author.id}, {prompt.replace('pox!','')}")
                    await self.process_commands(message)
                else:
                    if not message.author.bot or message.author.system:
                        if self.profanity_filter.is_profane(prompt):
                            
                            url = os.path.dirname(__file__)
                            url2 = os.path.join(url,"resources/nah.jpg")

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
                # log messages for making graphs of chat count in days or hours if i can
                # I'm not doing bad things, trust me
                # await self.db_connection.execute("INSERT INTO messages (id, content, user_id, timestamp, channel) VALUES (?, ?, ?, ?, ?)", (message.id, message.content, message.author.id, message.created_at.timestamp(), message.channel.id))
                
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
            self.processed_interactions += 1
            logger.info(f"{inter.user.display_name} issued {inter.command.name if inter.command else "Unknown"} on {inter.guild.name if inter.guild and inter.guild.name.strip() is not None else "Unknown"}.")
            if inter.command_failed:
                self.failed_interactions += 1
                logger.error("The requested command thrown error!")
                

    async def close(self) -> None:
        async with aiofiles.open("data/blacklisted_words.json", 'w+') as f:
            await f.write(json.dumps(self.blacklisted_words, indent=4))
        
        async with aiofiles.open("data/server_data.json", 'w+') as f:
            await f.write(json.dumps(self.servers_data, indent=4))

        if self.db_connection:
            await self.db_connection.commit()
            await self.db_connection.close()
            logger.debug("Database closed")
        
        return await super().close()
        
    def get_launch_time(self) -> datetime.datetime:
        return self.launch_time
    