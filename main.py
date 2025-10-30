import os
import subprocess
import uuid
import time
import discord

from datetime import datetime, UTC
from discord.ext import commands

import stuff
stuff.create_dir_if_not_exists("./logs")

#import help_command
from bot import PoxBot

from logger import logger

handled_messages = 0
current_guild = 0

start_time = time.time()

commit_hash = ""

try:
    output = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True, check=True)
    commit_hash = output.stdout.strip()
except subprocess.CalledProcessError as e:
    logger.error(f"Error occured: {e}")
except FileNotFoundError:
    logger.error("Git command not found. make sure to check if Git is installed.")

bot_token = stuff.get_bot_token()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

INACTIVITY_THRESHOLD = 300

bot = PoxBot(
    intents=intents,
    command_prefix=commands.when_mentioned_or("pox!"),
    owner_id=1321324137850994758,
    #chunk_guilds_at_startup=False,
    #member_cache_flags=discord.MemberCacheFlags.none()
)

tree = bot.tree

@tree.command(name="reload_cogs")
async def reload(interaction: discord.Interaction):
    for fname in os.listdir('./cogs'):
        if fname.endswith('.py'):
            logger.debug(f"Loading extension {fname[:-3]}")
            try:
                await bot.reload_extension(f'cogs.{fname[:-3]}')
            except Exception as e:
                logger.exception(f"Exception thrown while reloading extension {fname[:-3]}.")
    
    await bot.tree.sync()
    await interaction.response.send_message("Commands are reloaded!", ephemeral=True, delete_after=10)
    return

session_uuid = uuid.uuid4()

last_interaction = datetime.now(UTC)

namesignature = stuff.generate_namesignature()
last_commit_message = stuff.get_latest_commit_message()

if __name__ == "__main__":
    if not bot_token:
        print("You should to put the bot token to 'TOKEN' in .env!")
        exit()
    else:
        try:
            bot.run(bot_token, log_handler=None)
        except KeyboardInterrupt:
            print("Shutting down...")
            pass
        finally:
            print("Bot has been stopped")